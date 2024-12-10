import warnings
import time
import threading
import base64
import pickle
import sqlite3
from pathlib import Path

import tensorflow as tf
import numpy as np

import io
from PIL import Image
import shap

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
        # Initialize the explainer
        explainer = shap.Explainer(model)

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

            # Reload the explainer based on the new reloaded model
            explainer = shap.Explainer(model)

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

        # Calculate imapct values for tabular features using SHAP
        tabular_features_impacts = explainer(tabular_features)

        for i, job in enumerate(jobs_batch):
            feature_impacts = [
                {"feature": feature, "impact": value}
                for feature, value in zip(feature_names, tabular_features_impacts[i])
            ]
            job.feature_impact = feature_impacts

            # Compute Grad-CAM for each image
            predicted_class_index = np.argmax(predictions[i])
            heatmap = compute_grad_cam(
                model, resized_images[i : i + 1], predicted_class_index
            )

            # Encode heatmap as binary
            job.heatmap_binary = encode_heatmap_to_binary(heatmap)

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

            # Extract individual feature impacts
            impacts = {
                impact["feature"]: impact["impact"] for impact in job.feature_impact
            }
            impact_age = impacts.get("age", None)
            impact_localization = impacts.get("localization", None)
            impact_sex = impacts.get("sex", None)

            # Extract binary heatmap from the job
            heatmap_binary = getattr(job, "heatmap_binary", None)

            # Update database query
            cursor.execute(
                """
                UPDATE requests
                SET probability = ?, lesion_type = ?, model_id = ?, 
                    impact_age = ?, impact_localization = ?, impact_sex = ?, heatmap = ?
                WHERE request_id = ?;
                """,
                (
                    probability,
                    predicted_label,
                    model_version,
                    impact_age,
                    impact_localization,
                    impact_sex,
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


def compute_grad_cam(
    model, image, predicted_class_index, last_conv_layer_name="last_cnn_layer"
):
    """
    Compute Grad-CAM for a single image (Impact of different areas of the image as a heatmap).

    Args:
        model: Trained TensorFlow model.
        image: Preprocessed image (single image in batch format).
        predicted_class_index: Index of the predicted class.
        last_conv_layer_name: Name of the last convolutional layer in the model.

    Returns:
        Heatmap as a 2D numpy array.
    """
    grad_model = tf.keras.models.Model(
        inputs=model.input,
        outputs=[model.get_layer(last_conv_layer_name).output, model.output],
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image)
        loss = predictions[:, predicted_class_index]

    # Compute gradients of the predicted class with respect to the feature maps
    grads = tape.gradient(loss, conv_outputs)

    # Compute the mean intensity of gradients for each channel
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Multiply each channel by its importance and sum
    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(conv_outputs * pooled_grads, axis=-1)

    # Normalize heatmap
    heatmap = np.maximum(heatmap, 0)  # ReLU
    heatmap /= tf.reduce_max(heatmap)
    return heatmap.numpy()


def encode_heatmap_to_binary(heatmap):
    heatmap = (heatmap * 255).astype(np.uint8)  # Normalize
    img = Image.fromarray(heatmap)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()
