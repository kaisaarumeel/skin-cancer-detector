import time
import threading
#from ...application.views.jobs.state import PREDICTION_JOBS

from application.views.jobs.state import PREDICTION_JOBS

def manage_predictions():
    global PREDICTION_JOBS

    INTERVAL = 1 #TODO decide actual time / dynamic?

    while True:
        #TODO listen for event
            # if signalled, load model from DB
        
        #TODO read queue and prepare batch 

        #TODO preprocess image data function
        # read model input dimensions and pass images + dim as params

        #TODO call predict() on batch

        #TODO return results

        print("Processing batch of predictions...")

        # Sleep thread before restarting loop
        time.sleep(INTERVAL)



def start_prediction_manager():
    # Create separate thread that will manage predictions
    prediction_thread = threading.Thread(daemon=True, target=manage_predictions)
    
    # Initialise thread 
    prediction_thread.start()

