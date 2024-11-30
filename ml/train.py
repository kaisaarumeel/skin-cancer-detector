import os
import numpy as np
import matplotlib
import gc
from sklearn.utils import class_weight
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input,
    Dense,
    Dropout,
    concatenate,
    GlobalAveragePooling2D,
)
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.metrics import Recall, Precision
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import categorical_crossentropy

# Custom modules
from .cache import query_db_or_cache
from .plot import plot
from .persistence import save_model
from .tests import (
    validate_input_data,
    validate_preprocessed_data,
    validate_split_data,
    validate_model_output,
)
from .callbacks import StatusUpdateCallback
import time


# Check if the current environment has a display
# If not, use the Agg backend for matplotlib
backend = "TkAgg" if os.environ.get("DISPLAY") else "Agg"
matplotlib.use(backend)


def set_status(job, status):
    if job != None:
        job.status = status
    else:
        print(status)


def train(
    job=None,
    clear_cache=False,
    force_gpu=False,
    test=False,
    db_images_name="../db_images.sqlite3",
    db_app_name="../db_app.sqlite3",
    images_table_name="images",
    app_table_name="models",
    row_limit=None,
    start_row=0,
    test_size=0.2,
    random_state=666,
    input_size=(224, 224, 3),
    num_classes=7,
    dropout_rate=0.0,
    loss_function="categorical_crossentropy",
    num_epochs=10,
    batch_size=16,
    learning_rate=1e-5,
    malignant_multiplier=20.0,
):
    # Custom status callback for job status update
    status_callback = StatusUpdateCallback(job, set_status)

    if test:
        # Some testers might want to utilize their GPU
        if not force_gpu:
            # Disable GPU for testing
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
        # Pass the entire dataset
        batch_size = row_limit
        num_epochs = 1
        # We can't use too small of an image size
        # as the pre-trained model has a minimum size requirement
        # due to pooling layers
        input_size = (32, 32, 3)

    set_status(job, "Retrieving processed data, lesion_type_encoder, and images")

    # Retrieve processed data, lesion_type_encoder, and images
    processed_data, lesion_type_encoder, images = query_db_or_cache(
        clear_cache=clear_cache,
        test=test,
        db_name=db_images_name,
        images_table_name=images_table_name,
        row_limit=row_limit,
        start_row=start_row,
        requested_size=input_size[:2],
    )
    set_status(job, "Validating input data")
    validate_input_data(processed_data, images, input_size)

    # Constants used throughout the training process
    TEST_SIZE = test_size
    RANDOM_STATE = random_state
    INPUT_SIZE = input_size
    NUM_CLASSES = num_classes
    DROPOUT_RATE = dropout_rate
    LOSS_FUNCTION = loss_function
    NUM_EPOCHS = num_epochs
    BATCH_SIZE = batch_size
    LEARNING_RATE = learning_rate

    set_status(job, "Creating tabular features and labels")

    # Define the optimizer
    optimizer = Adam(learning_rate=LEARNING_RATE)

    # Extract tabular features and labels
    tabular_features = processed_data[["age", "localization", "sex_male"]]
    labels = processed_data["lesion_type"].values

    # Delete the processed_data to free up memory
    del processed_data
    gc.collect()

    # Create the tabular features by stacking all the values
    # into a single 2D array which will have columns: age, localization, sex_male
    tabular_features = np.column_stack(
        (
            tabular_features["age"].values,
            tabular_features["localization"].values,
            tabular_features["sex_male"].values,
        )
    )

    # Get the number of tabular features by accessing the number
    # of columns in the tabular_features array
    N_TABULAR_FEATURES = tabular_features.shape[1]

    # To ensure that the tabular features have an equal impact
    # onto the model, we will standardize the features
    scaler = StandardScaler()
    tabular_features_scaled = scaler.fit_transform(tabular_features)

    # Convert labels to categorical
    labels_cat = to_categorical(labels, num_classes=NUM_CLASSES)

    set_status(job, "Validating preprocessed data")
    validate_preprocessed_data(tabular_features_scaled, labels_cat, NUM_CLASSES)

    # Free up memory by deleting tabular_features
    del tabular_features
    gc.collect()

    set_status(job, "Splitting data into train and validation sets")
    # Create the split by splitting the data into train and validation sets
    # For now, we will only use the train and validation sets as we do not
    # have a broader dataset to split into train, validation, and test sets
    X_img_train, X_img_val, X_tab_train, X_tab_val, y_train, y_val = train_test_split(
        images,
        tabular_features_scaled,
        labels_cat,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels,
        shuffle=True,
    )

    validate_split_data(X_img_train, X_img_val, X_tab_train, X_tab_val, y_train, y_val)

    # Define the input layers for the model
    image_input = Input(shape=INPUT_SIZE)
    tabular_input = Input(shape=(N_TABULAR_FEATURES,))

    set_status(job, "Creating model")

    # Utilize a pre-trained model for abstract feature extraction
    pretrained = DenseNet121(
        weights="imagenet", include_top=False, input_tensor=image_input
    )

    # Set the pre-trained model's output to be the input
    # for the next layer
    x = pretrained.output
    # Add a GlobalAveragePooling2D layer to reduce the number of parameters
    x = GlobalAveragePooling2D()(x)
    # Add a Dense layer with ReLU activation to map the convolutional features
    # to the output space
    x = Dense(256, activation="relu")(x)
    # Add a Dropout layer to prevent overfitting
    x = Dropout(DROPOUT_RATE)(x)

    # Tabular features dont use convolutional layers
    y = Dense(128, activation="relu")(tabular_input)
    y = Dense(64, activation="relu")(y)

    # Combine the model axes
    combined_axes = concatenate([x, y])

    # Todo: Add more layers to the combined model
    # Add a Dense layer with ReLU activation to map the combined features
    z = Dense(256, activation="relu")(combined_axes)
    # Add a Dropout layer to prevent overfitting for the combined features
    z = Dropout(DROPOUT_RATE)(z)

    # Create an output layer with softmax activation for the number of classes
    output = Dense(NUM_CLASSES, activation="softmax")(z)

    # Create the finalized model
    model = Model(inputs=[image_input, tabular_input], outputs=output)

    validate_model_output(model, INPUT_SIZE, NUM_CLASSES)

    # Compute class weights to account for unbalanced classes and prioritize malignant conditions
    class_weights = class_weight.compute_class_weight(
        class_weight="balanced",  # Use balanced class weights
        classes=np.unique(labels),  # Extract the unique classes
        y=labels,  # Use the labels
    )

    # Create initial mapping of class indices to class weights
    class_weights = dict(enumerate(class_weights))

    class_names = lesion_type_encoder.inverse_transform(range(NUM_CLASSES))
    malignant_classes = ["akiec", "bcc", "mel"]

    MALIGNANT_MULTIPLIER = malignant_multiplier

    # Loop through class names
    for idx, class_name in enumerate(class_names):
        # Check if class name is in malignant classes
        if class_name in malignant_classes:
            # Multiply class weight by malignant multiplier
            class_weights[idx] *= MALIGNANT_MULTIPLIER

    set_status(job, "Compiling model")
    # Compile model
    model.compile(
        optimizer=optimizer,
        loss=LOSS_FUNCTION,
        metrics=["accuracy", Precision(name="precision"), Recall(name="recall")],
    )

    if test:
        print("Stopping early due to test mode")
        return

    set_status(job, "Training model")

    # If job is not None then set verbose to 0
    is_verbose = 1 if job == None else 0

    # Train the model on prepared data
    history = model.fit(
        x=[X_img_train, X_tab_train],  # Specify image and tabular training data
        y=y_train,  # Specify training labels
        batch_size=BATCH_SIZE,  # N samples passed through model before weight update
        epochs=NUM_EPOCHS,  # Specify number of epochs to train for
        validation_data=(
            [X_img_val, X_tab_val],
            y_val,
        ),  # Specify image and tabular validation data
        class_weight=class_weights,
        callbacks=[status_callback],
        verbose=is_verbose,
    )

    # Make predictions on the test set
    y_predicted = model.predict([X_img_val, X_tab_val])

    # Get the predicted classes by extracting the index with highest probability
    predicted_classes = np.argmax(y_predicted, axis=1)

    # Get the true classes by extracting the index with highest probability (which is 09)
    true_classes = np.argmax(y_val, axis=1)

    # Get actual class labels from lesion_type_encoder
    class_names = lesion_type_encoder.inverse_transform(range(NUM_CLASSES))

    # Define malignant and benign class indices. These will unlikely change.
    malignant_classes = ["akiec", "bcc", "mel"]

    # Get true and predicted class names
    true_class_names = lesion_type_encoder.inverse_transform(true_classes)
    predicted_class_names = lesion_type_encoder.inverse_transform(predicted_classes)

    # Create boolean masks for malignant classes by checking if class names are in malignant_classes
    is_true_malignant = np.isin(true_class_names, malignant_classes)
    is_predicted_malignant = np.isin(predicted_class_names, malignant_classes)

    # Calculate true positives and false negatives
    TP = np.sum(np.logical_and(is_true_malignant, is_predicted_malignant))
    FN = np.sum(
        np.logical_and(is_true_malignant, np.logical_not(is_predicted_malignant))
    )

    # Calculate Custom Recall
    custom_recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0

    print(f"Recall for malignant classes: {custom_recall:.4f}%")

    if job == None:
        # Dont plot if this is a server job
        # Plot classification report, confusion matrix, and training history
        plot(history, true_classes, predicted_classes, class_names)

    set_status(job, "Saving model")
    # Save model
    save_model(
        db_app_name,
        app_table_name,
        model,
        TEST_SIZE,
        INPUT_SIZE,
        DROPOUT_RATE,
        LOSS_FUNCTION,
        NUM_EPOCHS,
        BATCH_SIZE,
        LEARNING_RATE,
        history.history["val_accuracy"][-1],
        custom_recall,
    )
    print("Model saved successfully to database")
