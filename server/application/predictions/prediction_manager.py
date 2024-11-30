import warnings
import time
import threading
from pathlib import Path

import tensorflow as tf

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
    model = load_active_model_from_db(abs_db_path)

    # Predictions loop
    while True:
        # Sleep thread to periodically check Job queue and not block app execution
        time.sleep(INTERVAL)

        # Check if the model should be reloaded
        if model_reload_event.is_set() or model == None:
            print("Reloading model...")
            model = load_active_model_from_db(abs_db_path)

            # Clear the event for reuse
            model_reload_event.clear()

        # Check if there was an active model in the database
        # and that it was successfully loaded
        if model == None:
            warnings.warn(
                "Active model could not be loaded from database", category=UserWarning
            )
            # Skip this loop iteration to attempt to reload the model
            continue

        # Dequeue the Jobs to be processed, up to the max limit
        jobs_batch = [
            PREDICTION_JOBS.get()
            for _ in range(min(BATCH_SIZE, PREDICTION_JOBS.qsize()))
        ]

        # Prepare a list of resized images that fit the model input size
        resized_images = preprocess_images(
            extract_images(jobs_batch), get_model_input_shape(model)
        )

        # TODO Prepare input batch function call

        # TODO call predict() on batch

        # TODO return results

        print("Processing predictions...")


############################### HELPER FUNCTIONS ###############################


def start_prediction_manager():
    # Create separate thread that will manage predictions
    # daemon=True ensure thread is terminated alongside main thread
    prediction_thread = threading.Thread(daemon=True, target=manage_predictions)

    # Initialise thread
    prediction_thread.start()


def signal_model_reload():
    # Set event to signal model reload
    model_reload_event.set()


def extract_images(jobs):
    images = []
    for job in jobs:
        parameters = job.parameters
        image = parameters.get("image")
        images.append(image)

    return images


def get_model_input_shape(model):
    # Extract the input shape from the model
    target_input_shape = model.input_shape[0]

    # Extract target height and width from input shape tuple
    target_height, target_width = target_input_shape[1:3]

    # Return target height and width
    return (target_height, target_width)
