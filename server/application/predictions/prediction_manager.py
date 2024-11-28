import time
import threading

from application.views.jobs.state import PREDICTION_JOBS


# Event to signal model reload
model_reload_event = threading.Event()


def manage_predictions():
    global PREDICTION_JOBS  # Prediction Job queue
    INTERVAL = 1  # TODO decide actual time / dynamic?

    while True:
        # Check if model reload is signalled
        if model_reload_event.is_set():
            # TODO: call model reload function once implemented
            print("Reloading model...")

            # Clear the event
            model_reload_event.clear()

        # TODO read queue and prepare batch

        # TODO preprocess image data function
        # read model input dimensions and pass images + dim as params

        # TODO call predict() on batch

        # TODO return results

        print("Processing batch of predictions...")

        # Sleep thread before restarting loop
        time.sleep(INTERVAL)


def start_prediction_manager():
    # Create separate thread that will manage predictions
    prediction_thread = threading.Thread(daemon=True, target=manage_predictions)

    # Initialise thread
    prediction_thread.start()


def signal_model_reload():

    # Set Event to True to signal model reload
    model_reload_event.set()
