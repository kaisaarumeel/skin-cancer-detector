import warnings
import time
import threading
import base64
import pickle
import sqlite3
from pathlib import Path

import tensorflow as tf
import numpy as np

# Custom modules
from application.views.jobs.state import PREDICTION_JOBS
from application.mlsym.persistence import load_active_model_from_db
from .preprocess_user_data import (
    preprocess_images,
    extract_images,
    extract_tabular_features,
)


# Find the path to the database
abs_db_path = Path(__file__).resolve().parents[3] / "db_app.sqlite3"

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
        tabular_features = extract_tabular_features(
            jobs_batch, tabular_scaler, localization_encoder
        )

        # Run inference on the prepared batch
        predictions = model.predict([resized_images, tabular_features])

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
        conn.execute("BEGIN TRANSACTION")

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

            # Update database query
            cursor.execute(
                """
                UPDATE requests
                SET probability = ?, lesion_type = ?, model = ?
                WHERE request_id = ?;
                """,
                (probability, predicted_label, model_version, request_id),
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
