from django.test import TransactionTestCase
from application.models import Requests, Users
from application.predictions.prediction_manager import (
    delete_jobs_from_db,
    extract_jobs_from_queue,
)
import time
import threading
from queue import Empty
from application.views.jobs.state import PREDICTION_JOBS


class JobExpirationTests(TransactionTestCase):
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
        self.expired_request_1 = Requests.objects.create(
            request_id=1,
            created_at=0,  # Expired (UNIX timestamp start time in 1970)
            image=b"test_image_data",
            probability=None,
            localization="ear",
            lesion_type=None,
            user_id=self.mock_user,
            model=None,
        )
        self.expired_job_1 = MockJob(
            self.expired_request_1.request_id,
            self.expired_request_1.created_at,
            {"request_id": self.expired_request_1.request_id},
        )
        # Insert second expired Request record in DB and create Mock job
        self.expired_request_2 = Requests.objects.create(
            request_id=2,
            created_at=0,  # Expired (UNIX timestamp start time in 1970)
            image=b"test_image_data",
            probability=None,
            localization="ear",
            lesion_type=None,
            user_id=self.mock_user,
            model=None,
        )
        self.expired_job_2 = MockJob(
            self.expired_request_2.request_id,
            self.expired_request_2.created_at,
            {"request_id": self.expired_request_2.request_id},
        )

        # Insert valid Request record in DB and create Mock job
        self.valid_request_1 = Requests.objects.create(
            request_id=3,
            created_at=current_time,  # Valid (current time)
            image=b"test_image_data",
            probability=None,
            localization="ear",
            lesion_type=None,
            user_id=self.mock_user,
            model=None,
        )
        self.valid_job_1 = MockJob(
            self.valid_request_1.request_id,
            self.valid_request_1.created_at,
            {"request_id": self.valid_request_1.request_id},
        )
        # Insert second valid Request record in DB and create Mock job
        self.valid_request_2 = Requests.objects.create(
            request_id=4,
            created_at=current_time,  # Valid (current time)
            image=b"test_image_data_2",
            probability=None,
            localization="ear",
            lesion_type=None,
            user_id=self.mock_user,
            model=None,
        )
        self.valid_job_2 = MockJob(
            self.valid_request_2.request_id,
            self.valid_request_2.created_at,
            {"request_id": self.valid_request_2.request_id},
        )

    def set_up_jobs_in_queue(self):
        """
        Helper function to add Mock jobs to the global PREDICTION_JOBS queue.
        """
        # Clean up the queue if there are any leftover jobs
        while not (PREDICTION_JOBS.empty()):
            _ = PREDICTION_JOBS.get_nowait()
        # Enqueue the fresh jobs
        PREDICTION_JOBS.put(self.expired_job_1)
        PREDICTION_JOBS.put(self.valid_job_1)
        PREDICTION_JOBS.put(self.expired_job_2)
        PREDICTION_JOBS.put(self.valid_job_2)

    ##################################### TESTS #####################################

    def test_extract_valid_job_single(self):
        """
        Test that extract_jobs_from_queue correctly retrieves valid jobs.
        """
        BATCH_SIZE = 1
        JOB_EXPIRY_TIME = 900  # 15 minutes

        # Add Mock jobs to global queue
        self.set_up_jobs_in_queue()

        # Extract valid jobs from the global queue
        jobs_batch, _ = extract_jobs_from_queue(BATCH_SIZE, JOB_EXPIRY_TIME)

        # Assert that 1 valid jobs were retrieved
        self.assertEqual(len(jobs_batch), 1)
        self.assertEqual(
            jobs_batch[0].parameters["request_id"],
            self.valid_job_1.parameters["request_id"],
        )

    def test_extract_valid_jobs_multiple(self):
        """
        Test that extract_jobs_from_queue correctly retrieves valid jobs.
        """
        BATCH_SIZE = 2
        JOB_EXPIRY_TIME = 900  # 15 minutes

        # Add Mock jobs to global queue
        self.set_up_jobs_in_queue()

        # Extract valid jobs from the global queue
        jobs_batch, _ = extract_jobs_from_queue(BATCH_SIZE, JOB_EXPIRY_TIME)

        # Assert that 2 valid jobs were retrieved
        self.assertEqual(len(jobs_batch), 2)
        self.assertEqual(
            jobs_batch[0].parameters["request_id"],
            self.valid_job_1.parameters["request_id"],
        )
        self.assertEqual(
            jobs_batch[1].parameters["request_id"],
            self.valid_job_2.parameters["request_id"],
        )

    def test_extract_expired_job_single(self):
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
        self.assertEqual(expired_jobs[0], self.expired_job_1.parameters["request_id"])

    def test_extract_expired_jobs_multiple(self):
        """
        Test that extract_jobs_from_queue correctly identifies expired jobs.
        """
        BATCH_SIZE = 2
        JOB_EXPIRY_TIME = 900  # 15 minutes

        # Add Mock jobs to global queue
        self.set_up_jobs_in_queue()

        # Extract expired jobs from the global queue
        _, expired_jobs = extract_jobs_from_queue(BATCH_SIZE, JOB_EXPIRY_TIME)

        # Assert that the expired job was identified correctly
        self.assertEqual(len(expired_jobs), 2)  # two expired jobs
        self.assertEqual(expired_jobs[0], self.expired_job_1.parameters["request_id"])
        self.assertEqual(expired_jobs[1], self.expired_job_2.parameters["request_id"])

    def test_batch_size_limit_is_respected(self):
        """
        Test that a batch size smaller than the qsize correctly leaves elements in the queue.
        """
        BATCH_SIZE = 10
        JOB_EXPIRY_TIME = 900  # 15 minutes

        # Populate the global job queue
        for _ in range(0, BATCH_SIZE + 1):
            PREDICTION_JOBS.put(self.valid_job_1)

        # Extract valid jobs from the global queue
        jobs_batch, _ = extract_jobs_from_queue(BATCH_SIZE, JOB_EXPIRY_TIME)

        # Asser that the correct number of jobs were extracted
        self.assertEqual(BATCH_SIZE, len(jobs_batch))

        # Assert that the queue is not empty and that no exception is thrown
        try:
            self.assertIsNotNone(PREDICTION_JOBS.get(block=False))
        except Empty:
            self.fail(
                "Expected queue.get(block=False) to return a job, but it raised: queue.Empty."
            )

    def test_extract_empty_queue(self):
        """ "
        Test that the thread doesn't hang if the extract function is called when the queue is empty.
        """
        TIMEOUT = 5  # seconds
        BATCH_SIZE = 1
        JOB_EXPIRY_TIME = 900  # 15 minutes

        # Assert that the queue is empty before starting test
        self.assertTrue(PREDICTION_JOBS.empty())

        # List variables to hold the results
        jobs_batch = []
        expired_jobs = []

        # Wrapper function is needed to share the result variables between the two threads
        def target_wrapper():
            nonlocal jobs_batch, expired_jobs
            jobs_batch, expired_jobs = extract_jobs_from_queue(
                BATCH_SIZE, JOB_EXPIRY_TIME
            )

        # Run in daemon to ensure child thread gets terminated even if it hangs
        thread = threading.Thread(daemon=True, target=target_wrapper)
        thread.start()

        # Wait until the thread terminates or timeout happens
        thread.join(TIMEOUT)

        if thread.is_alive():
            self.fail(
                "The 'extract_jobs_from_queue' function timed out / hanged when called with an empty queue."
            )

        # Assert that the function returned empty lists
        self.assertEqual(jobs_batch, [])
        self.assertEqual(expired_jobs, [])

    def test_extract_jobs_batch_size_zero(self):
        """
        Test that a batch size of 0 doesn't break the job extractions function.
        """
        BATCH_SIZE = 0
        JOB_EXPIRY_TIME = 900  # 15 minutes

        self.set_up_jobs_in_queue()
        try:
            jobs_batch, expired_jobs = extract_jobs_from_queue(
                BATCH_SIZE, JOB_EXPIRY_TIME
            )
        except Exception as e:
            self.fail(
                f"extract_jobs_from_queue threw an exception due to batch size being 0 {e}"
            )

        # Assert nothing was returned
        self.assertEqual(len(jobs_batch), 0)
        self.assertEqual(len(expired_jobs), 0)

    def test_delete_single_job_from_db(self):
        """
        Test that delete_jobs_from_db successfully deletes a list with a single job from the database.
        """
        # Pass job id of the expired job to delete
        delete_jobs_from_db([self.expired_job_1.parameters["request_id"]])

        # Check if the expired job was deleted from the database
        with self.assertRaises(Requests.DoesNotExist):
            Requests.objects.get(request_id=self.expired_job_1.parameters["request_id"])

        # Check if the valid jobs still exist
        valid_job_1 = Requests.objects.get(
            request_id=self.valid_job_1.parameters["request_id"]
        )
        self.assertIsNotNone(valid_job_1)
        valid_job_2 = Requests.objects.get(
            request_id=self.valid_job_2.parameters["request_id"]
        )
        self.assertIsNotNone(valid_job_2)

    def test_delete_multiple_jobs_from_db(self):
        """
        Test that delete_jobs_from_db successfully deletes a list of multiple jobs from the database.
        """
        # Pass job ids of the expired jobs to delete
        delete_jobs_from_db(
            [
                self.expired_job_1.parameters["request_id"],
                self.expired_job_2.parameters["request_id"],
            ]
        )

        # Check if the expired jobs were deleted from the database
        with self.assertRaises(Requests.DoesNotExist):
            Requests.objects.get(request_id=self.expired_job_1.parameters["request_id"])
        with self.assertRaises(Requests.DoesNotExist):
            Requests.objects.get(request_id=self.expired_job_2.parameters["request_id"])

        # Check if the valid jobs still exist
        valid_job_1 = Requests.objects.get(
            request_id=self.valid_job_1.parameters["request_id"]
        )
        self.assertIsNotNone(valid_job_1)
        valid_job_2 = Requests.objects.get(
            request_id=self.valid_job_2.parameters["request_id"]
        )
        self.assertIsNotNone(valid_job_2)

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

    def test_delete_with_empty_job_id_list(self):
        """
        Test that calling delete_jobs_from_db with an empty list does nothing.
        """
        try:
            delete_jobs_from_db([])
            # Ensure no jobs are deleted
            self.assertEqual(
                Requests.objects.count(),
                4,  # Two jobs were created in setup
                "No jobs should be deleted when an empty list is passed.",
            )
        except Exception as e:
            self.fail(f"delete_jobs_from_db raised an exception for empty input: {e}")
