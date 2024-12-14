import warnings
import time
import threading
import base64
import pickle
import sqlite3
from pathlib import Path
import json
import tensorflow as tf
import numpy as np

import io
from PIL import Image

# Custom modules
from application.views.jobs.state import PREDICTION_JOBS
from application.mlsym.persistence import load_active_model_from_db
from .preprocess_user_data import (
    preprocess_images,
    extract_images,
    extract_tabular_features,
)


# Find the path to the database
abs_db_path = "../db_app.sqlite3"

# Event to signal model reload
model_reload_event = threading.Event()


def manage_predictions():
    global PREDICTION_JOBS  # Global Job queue
    BATCH_SIZE = 64  # Max number of jobs to process in one batch
    INTERVAL = 3  # TODO decide actual time / make dynamic?

    # Enable repeated warnings (otherwise subsequent matching warnings are silenced)
    warnings.simplefilter("always", UserWarning)

    # Load the active model from the database
    model, hyperparameters, model_version = load_active_model_from_db(abs_db_path)

    # Global explainer
    explainer = None

    if model != None:
        # Load the feature scaler and decoders
        tabular_scaler = get_scaler(hyperparameters)
        localization_encoder, lesion_type_encoder = get_encoders(hyperparameters)

    # Predictions loop
    while True:
        # Sleep thread to periodically check Job queue and not block app execution
        time.sleep(INTERVAL)

        # Check if the active model should be reloaded
        if model_reload_event.is_set() or model == None:
            print("Reloading model...")
            model, hyperparameters, model_version = load_active_model_from_db(
                abs_db_path
            )
            # Clear the event for reuse
            model_reload_event.clear()

            # Verify that the model was successfully loaded
            if model == None:
                warnings.warn(
                    "Active model could not be loaded from database",
                    category=UserWarning,
                )
                # Skip this loop iteration to attempt to reload the model
                continue

            # Reload the feature scaler and encoders
            tabular_scaler = get_scaler(hyperparameters)
            localization_encoder, lesion_type_encoder = get_encoders(hyperparameters)

        # Dequeue the Jobs to be processed, up to the max limit
        jobs_batch = [
            PREDICTION_JOBS.get()
            for _ in range(min(BATCH_SIZE, PREDICTION_JOBS.qsize()))
        ]

        # If there are no Jobs to be processed, skip this loop iteration
        if not jobs_batch:
            continue

        print("Processing predictions...")

        # Prepare resized images that fit the model input size
        resized_images = preprocess_images(
            extract_images(jobs_batch), get_model_input_shape(model)
        )

        # Extract the tabular features
        tabular_features, feature_names = extract_tabular_features(
            jobs_batch, tabular_scaler, localization_encoder
        )

        # Run inference on the prepared batch
        predictions = model.predict([resized_images, tabular_features])
        print("PREDICTION COMPLETED,")
        for i, job in enumerate(jobs_batch):
            predicted_class_index = np.argmax(predictions[i])

            # Prepare single-sample inputs for Grad-CAM
            image_input = np.expand_dims(
                resized_images[i], axis=0
            )  # Add batch dimension
            tabular_input = np.expand_dims(
                tabular_features[i], axis=0
            )  # Add batch dimension

            # Compute Grad-CAM with both inputs
            heatmap = compute_grad_cam(
                model,
                [image_input, tabular_input],
                predicted_class_index,
                original_image_shape=(
                    224,
                    224,
                ),  # Or whatever your original image size is
            )

            # We can calculate the importance of the image 
            # by taking the mean activation value for each pixel
            image_importance = np.mean(heatmap[0])

            # Compute feature importance for tabular data
            tabular_importances = compute_tabular_importance(
                model, [image_input, tabular_input], predicted_class_index
            )

            # Combine all importance values
            all_importances = np.concatenate([[image_importance], tabular_importances])
            
            # Calculate relative percentages
            total_importance = np.sum(np.abs(all_importances))
            relative_importances = (np.abs(all_importances) / total_importance) * 100

            # Encode heatmap as binary
            job.heatmap_binary = encode_heatmap_to_binary(heatmap)
            print("Heat map is processed.")



            # Map importance values to feature names
            job.feature_impact = {
                "image": float(relative_importances[0]),
                **{
                    name: float(importance)
                    for name, importance in zip(feature_names, relative_importances[1:])
                }
            }
            
            print(f"Feature impacts for job {job.job_id}:", job.feature_impact)
        # Update the requests table in the database with the results
        update_requests_in_db(
            abs_db_path, jobs_batch, predictions, lesion_type_encoder, model_version
        )

        ### END OF LOOP


############################### HELPER FUNCTIONS ###############################


def start_prediction_manager():
    # Create separate thread that will manage predictions
    # daemon=True ensures thread is terminated alongside main thread
    prediction_thread = threading.Thread(daemon=True, target=manage_predictions)

    # Initialise thread
    prediction_thread.start()


def signal_model_reload():
    # Set event to signal model reload
    model_reload_event.set()


def get_model_input_shape(model):
    # Extract the input shape from the model
    target_input_shape = model.input_shape[0]

    # Extract target height and width from input shape tuple
    target_height, target_width = target_input_shape[1:3]

    # Return target height and width
    return (target_height, target_width)


def get_scaler(hyperparameters):
    # Decode and unpickle the scaler
    encoded_scaler = hyperparameters["tabular_scaler"]
    pickled_scaler = base64.b64decode(encoded_scaler)

    # Return Scaler object
    return pickle.loads(pickled_scaler)


def get_encoders(hyperparameters):
    # Decode and unpickle the localization encoder
    encoded_loc_encoder = hyperparameters["localization_encoder"]
    pickled_loc_encoder = base64.b64decode(encoded_loc_encoder)
    localization_encoder = pickle.loads(pickled_loc_encoder)
    # Decode and unpickle the lesion_type encoder
    encoded_lesion_encoder = hyperparameters["lesion_type_encoder"]
    pickled_lesion_encoder = base64.b64decode(encoded_lesion_encoder)
    lesion_type_encoder = pickle.loads(pickled_lesion_encoder)

    # Return Encoder objects
    return localization_encoder, lesion_type_encoder


def update_requests_in_db(
    db_path, jobs_batch, predictions, lesion_type_encoder, model_version
):
    """
    Update the Requests table with the predictions for the given Jobs batch.
    """

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Prepare Request table updates
        for job, prediction in zip(jobs_batch, predictions, strict=True):
            # Extract the request id from the job_id as they are the same
            request_id = job.job_id
            # Extract the probability of the predicted class
            probability = float(np.max(prediction))

            # Get the index of the predicted class
            predicted_class_index = np.argmax(prediction)
            # Decode the label (return value is a list so we access the first element)
            predicted_label = lesion_type_encoder.inverse_transform(
                [predicted_class_index]
            )[0]

            # Convert job.feature_impact to JSON string
            ser_feature_impact = json.dumps(job.feature_impact)


            # Extract binary heatmap from the job
            heatmap_binary = getattr(job, "heatmap_binary", None)

            # Update database query
            cursor.execute(
                """
                UPDATE requests
                SET probability = ?, lesion_type = ?, model_id = ?, 
                    feature_impact = ?, heatmap = ?
                WHERE request_id = ?;
                """,
                (
                    probability,
                    predicted_label,
                    model_version,
                    ser_feature_impact,
                    heatmap_binary,
                    request_id,
                ),
            )

        # Commit database transaction
        conn.commit()
    except Exception as e:
        # Rollback if there was an error
        conn.rollback()
        print(f"Error updating database request table: {e}")
        # TODO error handling of processed jobs, add to some other queue?
    finally:
        # Close database connection
        conn.close()


def compute_tabular_importance(model, inputs, predicted_class_index):
    # By utilizing the gradient tape we track the gradient/derivative
    # and can calculate its importance

    # Ensure inputs are tensors with valid data types
    image_input = tf.convert_to_tensor(inputs[0], dtype=tf.float32)
    tabular_input = tf.convert_to_tensor(inputs[1], dtype=tf.float32)

    # Create new tape to record all tensor operations
    with tf.GradientTape() as tape:
        # Ensure we only watch the tabular_input tensor
        tape.watch(tabular_input)
        # Invoke a prediction without using the predict wrapper
        # as that doesnt allow us to track the gradient
        pred = model([image_input, tabular_input])
        # Retrieve the first batch prediction
        first_batch_prediction = pred[0, predicted_class_index]

    # Calculate partial derivative with respect to
    # each input feature in the tabular data.
    # We do this because this tells use how much the 
    # first batch prediction changes when we change
    # the input feature by a small amount
    gradients = tape.gradient(first_batch_prediction, tabular_input)

    # Calculate the feature importance by taking the absolute value
    # of all the gradients. We do this because we are only interested
    # in the magnitude of the impact of each feature
    feature_importance = tf.abs(gradients).numpy()[0]

    return feature_importance


def compute_grad_cam(model, inputs, predicted_class_index, original_image_shape):
    import cv2
    import numpy as np

    # Get the last conv layer from DenseNet121
    last_conv_layer = model.get_layer("conv5_block16_2_conv")

    # Create an instance of the model that returns the same shape
    # as the last conv layer and the model output.
    # We cant reuse the model as it has a different output shape
    grad_model = tf.keras.models.Model(
        inputs=model.inputs, outputs=[last_conv_layer.output, model.output]
    )

    with tf.GradientTape() as tape:
        # We dont need to track the features here 
        # as that is done automatically because these layers
        # are trainable
        conv_outputs, predictions = grad_model(inputs)
        # Select all probabilities for the predicted class
        # for all samples in the batch
        all_batch_predictions = predictions[:, predicted_class_index]

    # Calculate derivative of the predicted class
    # with respect to the conv layer features.
    # The higher this value the more the output would change
    # if we change that particular feature
    derivatives = tape.gradient(all_batch_predictions, conv_outputs)

    # For each conv feature calculate its importance
    # for the predicted class across the entire image
    average_derivative = tf.reduce_mean(derivatives, axis=(0, 1, 2))

    # Reshape so that they are compatible with outputs of
    # the convolutional layer to calculate impact for each feature
    average_derivative = tf.reshape(average_derivative, (1, 1, 1, -1))

    # Calculate the weighted sum of the conv outputs
    # This operation basically promotes features that have
    # high activation value for the predicted class
    # and also a high derivative whilst suppressing others
    weighted_conv_outputs = conv_outputs * average_derivative

    # Calculate the heatmap by summing all the weighted outputs
    # per pixel
    heatmap = tf.reduce_sum(weighted_conv_outputs, axis=-1)

    # Convert heatmap to numpy array
    heatmap = heatmap.numpy()

    # Remove negatives
    heatmap = np.maximum(heatmap, 0)

    # Normalize heatmap by rescaling it from 0 to 1
    heatmap = heatmap / (np.max(heatmap) + 1e-7)  # Use 1e-7 to avoid division by zero

    # Convert heatmap to 0-255 range
    heatmap = np.uint8(255 * heatmap)

    # Resize heatmap to match original image size
    heatmap = cv2.resize(heatmap, (original_image_shape[1], original_image_shape[0]))

    # Take the first channel only for heatmap
    heatmap = heatmap[:, :, 0]

    # Convert heatmap to RGB
    heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    # Get the original image from inputs
    original_img = inputs[0][0]  # Already a numpy array, just remove batch dimension

    # Normalize image so 0-255 range as it was rescaled to -1 to 1
    # for model input earlier
    original_img = (original_img * 255).astype(np.uint8)

    # Add the heatmap as a layer on top of the original image
    # with a weight of 0.6 for the original image and 0.4 for the heatmap.
    # The weights is how much each layer should be visible
    layered = cv2.addWeighted(original_img, 0.6, heatmap_colored, 0.4, 0)

    return heatmap, heatmap_colored, layered


def encode_heatmap_to_binary(heatmap_tuple):
    import cv2

    layered_image = heatmap_tuple[2]
    _, encoded_img = cv2.imencode(".png", layered_image)
    return encoded_img.tobytes()
