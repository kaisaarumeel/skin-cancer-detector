from django.http import JsonResponse
import threading
import time
import uuid
from ...decorators import admin_only, load_json
from ...mlsym.train import train
from django.views import View
from inspect import signature
from .job import Job
train_sig = signature(train)

# Global array to store training jobs
TRAINING_JOBS = []




# Wrapper function to train the model
def train_wrapper(job, train_args):
    try:
        # Train the model with the given arguments
        modified_args = {
            **train_args,  # Unpack all original arguments
            "job": job  # Add the job container
        }
        train(**modified_args)
        # Update job status to completed when training is done
        job.status = "completed"
    except Exception as e:
        # If an error occurs, update job status to failed and store the error message
        job.status = "failed"
        job.error = str(e)


class Retrain(View):
    @admin_only
    @load_json
    def post(self, request):
        global TRAINING_JOBS
        # These are the required fields for the training process
        required_fields = [
            "clear_cache",
            "force_gpu",
            "test",
            "db_images_name",
            "db_app_name",
            "images_table_name",
            "app_table_name",
            "row_limit",
            "start_row",
            "test_size",
            "random_state",
            "input_size",
            "num_classes",
            "dropout_rate",
            "loss_function",
            "num_epochs",
            "batch_size",
            "learning_rate",
        ]
        # Check if all required fields exist in request.data
        if not all(field in request.data for field in required_fields):
            return JsonResponse({"err": "Missing fields"}, status=400)

        # Package the request data into a dictionary
        train_args = {
            "clear_cache": request.data["clear_cache"],
            "force_gpu": request.data["force_gpu"],
            "test": request.data["test"],
            "db_images_name": request.data["db_images_name"],
            "db_app_name": request.data["db_app_name"],
            "images_table_name": request.data["images_table_name"],
            "app_table_name": request.data["app_table_name"],
            "row_limit": request.data["row_limit"],
            "start_row": request.data["start_row"],
            "test_size": request.data["test_size"],
            "random_state": request.data["random_state"],
            "input_size": request.data["input_size"],
            "num_classes": request.data["num_classes"],
            "dropout_rate": request.data["dropout_rate"],
            "loss_function": request.data["loss_function"],
            "num_epochs": request.data["num_epochs"],
            "batch_size": request.data["batch_size"],
            "learning_rate": request.data["learning_rate"],
        }

        # Get non-None values from request
        filtered_train_args = dict(
            filter(lambda item: item[1] is not None, train_args.items())
        )

        # Get default values from the training function signature
        default_values = lambda: {
            param.name: param.default
            for param in train_sig.parameters.values()
            if param.default is not param.empty
        }

        # Merge defaults with filtered args (filtered args will take precedence)
        merged_args = {**default_values(), **filtered_train_args}

        # Convert input_size to tuple if it's a list since
        # we do not have tuples in JSON
        if isinstance(merged_args.get("input_size"), list):
            merged_args["input_size"] = tuple(merged_args["input_size"])

        try:
            # Generate a unique job ID
            job_id = str(uuid.uuid4())
            
            # Add the job ID to the arguments
            merged_args["job"] = job_id
            
            # Create a new Job object and add it to the global array
            job = Job(
                job_id=job_id, start_time=int(time.time()), parameters=merged_args
            )
            TRAINING_JOBS.append(job)

            # Spawn a new thread to train the model
            train_thread = threading.Thread(
                target=train_wrapper, args=(job, merged_args)
            )
            # Daemonize the thread as it does not need graceful shutdown 
            # in most cases
            train_thread.daemon = True
            train_thread.start()

            return JsonResponse(
                {
                    "message": "Training process started successfully",
                    "job_id": job_id,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse(
                {"err": f"Failed to start training process: {str(e)}"}, status=500
            )

    @admin_only
    # Returns all training jobs
    def get(self, request):
        global TRAINING_JOBS
        return JsonResponse({"jobs": [job.to_dict() for job in TRAINING_JOBS]})

    # Deletes all completed jobs
    @admin_only
    def delete(self, request):
        global TRAINING_JOBS
        TRAINING_JOBS = [job for job in TRAINING_JOBS if job.status != "completed"]
        return JsonResponse({"message": "Deleted all completed jobs"}, status=204)
