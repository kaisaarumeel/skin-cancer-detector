from django.test import TestCase
from application.models import Requests, Users
from application.predictions.prediction_manager import (
    delete_jobs_from_db,
    extract_jobs_from_queue,
)
import time
from queue import Empty
from application.views.jobs.state import PREDICTION_JOBS


class JobExpirationTests(TestCase):
    def setUp(self):
        """
        Set up test data for requests.
        """

        # Global Job queue, accessible by the extract_jobs_from_queue function
        global PREDICTION_JOBS

        # Mock job class to simulate the job objects
        class MockJob:
            def __init__(self, job_id, start_time, parameters):
                self.job_id = job_id
                self.start_time = start_time
                self.parameters = parameters

        # Insert test jobs into the temporary database
        current_time = int(time.time())

        self.mock_user = Users.objects.create(
            username="testuser",
            is_admin=False,
            age=30,
            sex="male",
            password="testpassword",
        )

        # Insert expired Request record in DB and create Mock job
        self.expired_request = Requests.objects.create(
            request_id=1,
            created_at=0,  # Expired (UNIX timestamp start time in 1970)
            image=b"test_image_data",
            probability=None,
            localization="ear",
            lesion_type=None,
            user_id=self.mock_user,
            model_id=None,
        )
        self.expired_job = MockJob(
            self.expired_request.request_id,
            self.expired_request.created_at,
            {"request_id": self.expired_request.request_id},
        )

        # Insert valid Request record in DB and create Mock job
        self.valid_request = Requests.objects.create(
            request_id=2,
            created_at=current_time,  # Valid (current time)
            image=b"test_image_data",
            probability=None,
            localization="ear",
            lesion_type=None,
            user_id=self.mock_user,
            model_id=None,
        )
        self.valid_job = MockJob(
            self.valid_request.request_id,
            self.valid_request.created_at,
            {"request_id": self.valid_request.request_id},
        )

    def set_up_jobs_in_queue(self):
        """
        Helper function to add Mock jobs to the global PREDICTION_JOBS queue.
        """
        PREDICTION_JOBS.put(self.expired_job)
        PREDICTION_JOBS.put(self.valid_job)

    ##################################### TESTS #####################################

    def test_extract_valid_jobs(self):
        """
        Test that extract_jobs_from_queue correctly retrieves valid jobs.
        """
        BATCH_SIZE = 1
        JOB_EXPIRY_TIME = 900  # 15 minutes

        # Add Mock jobs to global queue
        self.set_up_jobs_in_queue()

        # Extract valid jobs from the global queue
        jobs_batch, _ = extract_jobs_from_queue(BATCH_SIZE, JOB_EXPIRY_TIME)

        # Assert that 1 valid job was retrieved
        self.assertEqual(len(jobs_batch), 1)
        self.assertEqual(
            jobs_batch[0],
            self.valid_job,
        )

    def test_extract_expired_jobs(self):
        """
        Test that extract_jobs_from_queue correctly identifies expired jobs.
        """
        BATCH_SIZE = 1
        JOB_EXPIRY_TIME = 900  # 15 minutes

        # Add Mock jobs to global queue
        self.set_up_jobs_in_queue()

        # Extract expired jobs from the global queue
        _, expired_jobs = extract_jobs_from_queue(BATCH_SIZE, JOB_EXPIRY_TIME)

        # Assert that the expired job was identified correctly
        self.assertEqual(len(expired_jobs), 1)  # One expired job
        self.assertEqual(expired_jobs[0], self.expired_job.parameters["request_id"])

    def test_batch_size_limit_is_respected(self):
        """
        Test that a batch size smaller than the qsize correctly leaves elements in the queue.
        """
        BATCH_SIZE = 10
        JOB_EXPIRY_TIME = 900  # 15 minutes

        # Populate the global job queue
        for _ in range(0, BATCH_SIZE + 1):
            PREDICTION_JOBS.put(self.valid_job)

        # Extract valid jobs from the global queue
        jobs_batch, _ = extract_jobs_from_queue(BATCH_SIZE, JOB_EXPIRY_TIME)

        # Asser that the correct number of jobs were extracted
        self.assertEqual(BATCH_SIZE, len(jobs_batch))

        # Assert that the queue is not empty and that no exception is thrown
        try:
            self.assertIsNotNone(PREDICTION_JOBS.get(block=False))
        except Empty:
            self.fail(
                "Expected queue.get(block=False) to return a job, but it raised queue.Empty."
            )

    def test_delete_jobs_from_db(self):
        """
        Test that delete_jobs_from_db successfully deletes jobs from the database.
        """
        # Pass job ids of the expired job to delete
        delete_jobs_from_db([self.expired_job.parameters["request_id"]])

        # Check if the expired job was deleted from the database
        with self.assertRaises(Requests.DoesNotExist):
            Requests.objects.get(request_id=self.expired_job.parameters["request_id"])

        # Check if the valid job still exists
        valid_job = Requests.objects.get(
            request_id=self.valid_job.parameters["request_id"]
        )
        self.assertIsNotNone(valid_job)

    def test_delete_non_existent_job(self):
        """
        Test that attempting to delete a non-existent job does not raise an error.
        """
        try:
            # Call the delete function with a non-existent job ID
            delete_jobs_from_db([999])
        except Exception as e:
            self.fail(
                f"delete_jobs_from_db raised an exception for non-existent job: {e}"
            )

    def test_delete_with_empty_job_ids(self):
        """
        Test that calling delete_jobs_from_db with an empty list does nothing.
        """
        try:
            delete_jobs_from_db([])
            # Ensure no jobs are deleted
            self.assertEqual(
                Requests.objects.count(),
                2,  # Two jobs were created in setUp
                "No jobs should be deleted when an empty list is passed.",
            )
        except Exception as e:
            self.fail(f"delete_jobs_from_db raised an exception for empty input: {e}")
