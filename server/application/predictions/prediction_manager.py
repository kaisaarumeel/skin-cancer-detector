import warnings
import time
import threading
import base64
import pickle
from pathlib import Path

import tensorflow as tf
import numpy as np

# Custom modules
from application.views.jobs.state import PREDICTION_JOBS
from application.mlsym.persistence import load_active_model_from_db
from .preprocess_user_images import preprocess_images


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
    model, hyperparameters = load_active_model_from_db(abs_db_path)

    if model != None:
        # Load the feature scaler and localization decoder
        tabular_scaler = getScaler(hyperparameters)
        localization_encoder = getEncoder(hyperparameters)

    # Predictions loop
    while True:
        # Sleep thread to periodically check Job queue and not block app execution
        time.sleep(INTERVAL)

        # Check if the active model should be reloaded
        if model_reload_event.is_set() or model == None:
            print("Reloading model...")
            model, hyperparameters = load_active_model_from_db(abs_db_path)
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

            # Reload the feature scaler and localization encoder
            tabular_scaler = getScaler(hyperparameters)
            localization_encoder = getEncoder(hyperparameters)

        # Dequeue the Jobs to be processed, up to the max limit
        jobs_batch = [
            PREDICTION_JOBS.get()
            for _ in range(min(BATCH_SIZE, PREDICTION_JOBS.qsize()))
        ]

        # If there are no Jobs to be processed, skip this loop iteration
        if not jobs_batch:
            continue

        # Prepare resized images that fit the model input size
        resized_images = preprocess_images(
            extract_images(jobs_batch), get_model_input_shape(model)
        )

        # Extract the tabular features
        tabular_features = extract_tabular_features(
            jobs_batch, tabular_scaler, localization_encoder
        )

        # TODO call predict() on batch
        ### NOTE: if prediction doesn't work, uncomment weights statement inside ml/persistence.py

        # TODO map results to request_ids and write them to database

        print("Processing predictions...")


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


def getScaler(hyperparameters):
    # Decode and unpickle the scaler
    encoded_scaler = hyperparameters["tabular_scaler"]
    pickled_scaler = base64.b64decode(encoded_scaler)

    # Return Scaler object
    return pickle.loads(pickled_scaler)


def getEncoder(hyperparameters):
    # Decode and unpickle the encoder
    encoded_encoder = hyperparameters["localization_encoder"]
    pickled_encoder = base64.b64decode(encoded_encoder)

    # Return Encoder object
    return pickle.loads(pickled_encoder)


def extract_images(jobs):
    # Extract images using list comprehension
    images = [job.parameters.get("image") for job in jobs]

    # Stack images in 2D array
    images = np.column_stack((images))

    return images


def extract_tabular_features(jobs, scaler, localization_encoder):
    # Extract features using list comprehension
    ages = [job.parameters.get("age") for job in jobs]
    localizations = [job.parameters.get("localization") for job in jobs]
    sexes = [job.parameters.get("sex").lower() == "male" for job in jobs]

    # Encode the localization labels
    localizations = localization_encoder.transform(localizations)

    # TODO one-hot encode localization

    # Stack features in 2D array
    tabular_features = np.column_stack((ages, localizations, sexes))

    # Standardize the distribution using the scaler
    tabular_features = scaler.transform(tabular_features)

    return tabular_features
