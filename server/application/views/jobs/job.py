class Job:
    # Initialize a Job object
    def __init__(self, job_id, start_time, parameters):
        self.job_id = job_id
        self.start_time = start_time
        self.parameters = parameters
        self.status = "running"
        self.error = None

    # Convert TrainingJob object to dictionary
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "start_time": self.start_time,
            "parameters": self.parameters,
            "status": self.status,
            "error": self.error,
        }

