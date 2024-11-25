import time
import threading

# Global array to store prediction jobs
PREDICTION_JOBS = []


class Prediction:
    def __init__(self, job_id, start_time, parameters):
        self.job_id = job_id
        self.start_time = start_time
        self.parameters = parameters
        self.status = "pending"  # Job status: pending, completed, failed
        self.result = None  # Store the result after processing
        self.error = None  # Store error message if any

    def to_dict(self):
        """Return a dictionary representation of the job."""
        return {
            "job_id": self.job_id,
            "start_time": self.start_time,
            "parameters": self.parameters,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


# Function to process prediction jobs
def process_prediction_job(job):
    try:
        # Simulate prediction processing time
        time.sleep(2)  # Example delay to simulate work

        # TODO: implemet actual logic of prediction here
        # For now, we'll just mock a result
        result = {
            "prediction": "benign",
            "probability": 0.95,
        }

        # Update the job's status and result
        job.status = "completed"
        job.result = result

    except Exception as e:
        # If an error occurs, update the job status to failed
        job.status = "failed"
        job.error = str(e)


def add_prediction_job(parameters):
    """
    Create a new prediction job, add it to the global array,
    and start processing it in a background thread.
    """
    global PREDICTION_JOBS

    # Create a new prediction job
    job = Prediction(parameters)

    # Add the job to the global array
    PREDICTION_JOBS.append(job)

    # Start a new thread to process the job
    prediction_thread = threading.Thread(target=process_prediction_job, args=(job,))
    prediction_thread.daemon = True  # Daemonize the thread
    prediction_thread.start()

    return job
