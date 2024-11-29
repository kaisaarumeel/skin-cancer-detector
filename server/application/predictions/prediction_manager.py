import warnings
import time
import threading
from pathlib import Path

import tensorflow as tf

# Custom modules
from application.views.jobs.state import PREDICTION_JOBS
from application.mlsym.persistence import load_active_model_from_db
from .resize_images import preprocess_images


# Find the path to the database
abs_db_path = Path(__file__).resolve().parents[3] / "db_app.sqlite3"

# Event to signal model reload
model_reload_event = threading.Event()


def manage_predictions():
    global PREDICTION_JOBS  # Prediction Job queue
    INTERVAL = 1  # TODO decide actual time / dynamic?

    # Enable repeated warnings (otherwise matching warnings are silenced)
    warnings.simplefilter("always", UserWarning)

    # Load the active model from the database
    model = load_active_model_from_db(abs_db_path)

    # Predictions loop
    while True:
        # Sleep thread to periodically check queue and not block app execution
        time.sleep(INTERVAL)

        # Check if the model should be reloaded
        if model_reload_event.is_set() or model == None:
            print("Reloading model...")
            model = load_active_model_from_db(abs_db_path)

            # Clear the event for reuse
            model_reload_event.clear()

        # If there was no active model,
        if model == None:
            warnings.warn(
                "Active model could not be loaded from database", category=UserWarning
            )
            # Skip this iteration to attempt to reload the model
            continue

        # TODO read queue and prepare batch

        # Preprocess image data 
        # TODO replace the hardcoded image paths with image list
        image_path = Path(__file__).resolve().parent / "image.jpg"
        image2_path = Path(__file__).resolve().parent / "image2.png"
        preprocess_images([str(image_path), str(image2_path)], model)


        # TODO call predict() on batch

        # TODO return results

        print("Processing predictions...")


def start_prediction_manager():
    # Create separate thread that will manage predictions
    prediction_thread = threading.Thread(daemon=True, target=manage_predictions)

    # Initialise thread
    prediction_thread.start()


def signal_model_reload():

    # Set Event to True to signal model reload
    model_reload_event.set()
