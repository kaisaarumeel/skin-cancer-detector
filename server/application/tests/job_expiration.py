from django.test import TestCase
from application.models import Requests, Users
from application.predictions.prediction_manager import (
    delete_jobs_from_db,
    JOB_EXPIRY_TIME,
)
import time


class JobExpirationTests(TestCase):
    def setUp(self):
        """
        Set up test data for requests.
        """
        # Insert test jobs into the temporary database
        current_time = int(time.time())

        self.mock_user = Users.objects.create(
            username="testuser",
            is_admin=False,
            age=30,
            sex="male",
            password="testpassword",
        )
        self.expired_job = Requests.objects.create(
            request_id=1,
            created_at=current_time - (JOB_EXPIRY_TIME + 10),  # Expired
            image=b"test_image_data",
            probability=None,
            localization="ear",
            lesion_type=None,
            user_id=self.mock_user,
            model_id=None,
        )
        self.valid_job = Requests.objects.create(
            request_id=2,
            created_at=current_time - 100,  # Valid
            image=b"test_image_data",
            probability=None,
            localization="ear",
            lesion_type=None,
            user_id=self.mock_user,
            model_id=None,
        )

    def test_delete_expired_jobs(self):
        """
        Test that jobs older than the expiration time are deleted.
        """
        # Collect job IDs to delete
        expired_job_ids = [self.expired_job.request_id]

        # Call the function to delete expired jobs
        delete_jobs_from_db(expired_job_ids)

        # Assert that the expired job is deleted
        self.assertFalse(
            Requests.objects.filter(request_id=self.expired_job.request_id).exists(),
            "Expired job should not exist after deletion.",
        )

        # Assert that the valid job still exists
        self.assertTrue(
            Requests.objects.filter(request_id=self.valid_job.request_id).exists(),
            "Valid job should still exist after expired job deletion.",
        )

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
