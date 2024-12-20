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
from application.models import Requests


# Find the path to the database
abs_db_path = "../db_app.sqlite3"

# Event to signal model reload
model_reload_event = threading.Event()


def manage_predictions():
    global PREDICTION_JOBS  # Global Job queue
    BATCH_SIZE = 64  # Max number of jobs to process in one batch
    INTERVAL = 3  # TODO decide actual time / make dynamic?
    JOB_EXPIRY_TIME = 15 * 60  # Expiry time for pending jobs (in seconds)

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

        # Extract jobs from the global queue
        jobs_batch, expired_jobs = extract_jobs_from_queue(BATCH_SIZE, JOB_EXPIRY_TIME)

        # Delete expired jobs (Request records) from the database
        if expired_jobs:
            delete_jobs_from_db(expired_jobs)

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

        try:
            predictions,valid_indices = process_predictions(model, resized_images, tabular_features)

            for batch_idx, original_idx in enumerate(valid_indices):
                job = jobs_batch[original_idx]
                prediction = predictions[batch_idx]                
                predicted_class_index = np.argmax(prediction)

                # Prepare single-sample inputs for Grad-CAM
                image_input = np.expand_dims(resized_images[original_idx], axis=0)
                tabular_input = np.expand_dims(tabular_features[original_idx], axis=0)

                # Compute grad cam for the image
                heatmap = compute_grad_cam(
                    model,
                    [image_input, tabular_input],
                    predicted_class_index,
                    original_image_shape=(
                        224,
                        224,
                    ),
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
                # we dont care about direction only magnitude
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
                    },
                }
            valid_jobs=[jobs_batch[i] for i in valid_indices]
            valid_predictions=predictions
            if valid_jobs:
                # Update the requests table in the database with the results
                update_requests_in_db(
                    abs_db_path, valid_jobs, valid_predictions, lesion_type_encoder, model_version
                )
            # Log failed predictions
            failed_indices = set(range(len(jobs_batch))) - set(valid_indices)
            if failed_indices:
                failed_job_ids = [jobs_batch[i].parameters["request_id"] for i in failed_indices]
                print(f"Failed to process jobs with IDs: {failed_job_ids}")
        except Exception as e:
            print(f"Error during prediction processing: {e}")
            continue

############################### HELPER FUNCTIONS ###############################

def process_predictions(model, resized_images, tabular_features):
    try:
        # First we try to perform predictions on the entire batch
        predictions = model.predict([resized_images, tabular_features])
        # If success then the indices remain the same
        valid_indices = list(range(len(resized_images)))
        return predictions, valid_indices
    except Exception as e:
        print(f"Batch prediction failed: {e}. Falling back to individual processing...")
        
        # If batch prediction fails, process each image individually
        # throwing out failed predictions
        predictions = []
        valid_indices = []
        
        for i in range(len(resized_images)):
            try:
                # Retrieve single image and tabular input
                image_input = np.expand_dims(resized_images[i], axis=0)
                tabular_input = np.expand_dims(tabular_features[i], axis=0)
                
                # Perform the prediction
                pred = model.predict([image_input, tabular_input])
                
                # Store successful prediction and its index
                # so that the rest of the function can find it
                predictions.append(pred[0])
                valid_indices.append(i)
                
            except Exception as individual_error:
                print(f"Failed to process image {i}: {individual_error}")
                continue
        
        # Convert predictions list back to numpy array 
        # to match the original shape
        if predictions:
            predictions = np.array(predictions)
            
        # Return the predictions and valid indices
        return predictions, valid_indices


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


def extract_jobs_from_queue(BATCH_SIZE, JOB_EXPIRY_TIME):
    """
    Extracts a batch of valid jobs from the queue and identifies expired jobs.

    This function dequeues jobs from the global queue (`PREDICTION_JOBS`) up to the
    specified `BATCH_SIZE`, checks if any are expired based on `JOB_EXPIRY_TIME`,
    and returns two lists:
    1. A list of valid job objects.
    2. A list of expired job IDs for deletion.

    Args:
        BATCH_SIZE (int): Maximum number of jobs to retrieve.
        JOB_EXPIRY_TIME (int): Expiry time for pending jobs (seconds)

    Returns:
        tuple: A tuple containing:
            - List of valid job objects.
            - List of expired job IDs.
    """

    current_time = time.time()  # Current UNIX timestamp

    jobs_batch = []  # List to collect valid jobs
    expired_jobs = []  # List to collect expired job IDs

    # Dequeue valid jobs and check for expired ones
    while not PREDICTION_JOBS.empty() and len(jobs_batch) < BATCH_SIZE:
        job = PREDICTION_JOBS.get()  # Dequeue the next job from the queue

        # Check if the job is expired using its start_time
        if current_time - job.start_time > JOB_EXPIRY_TIME:
            job_id = job.parameters["request_id"]
            print(
                f"Job {job_id} expired. Deleting corresponding Request record from database..."
            )

            # Collect job ID for deletion
            expired_jobs.append(job_id)
        else:
            # Append valid job objects to the batch
            jobs_batch.append(job)

    return jobs_batch, expired_jobs


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
                SET probability = ?, lesion_type = ?, model = ?, 
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


def delete_jobs_from_db(job_ids):
    """Delete jobs from the database based on their job_ids."""
    try:
        Requests.objects.filter(request_id__in=job_ids).delete()
        print(f"Jobs {job_ids} deleted successfully.")
    except Exception as e:
        print(f"Error deleting jobs {job_ids}: {e}")


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
