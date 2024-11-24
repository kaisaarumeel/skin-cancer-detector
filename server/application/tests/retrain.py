from django.test import TestCase, Client
from django.urls import reverse
from ..models import Users
import json
from django.contrib.auth.hashers import make_password
import time


class RetrainTests(TestCase):
    def setUp(self):
        # Create test admin user for login
        self.admin_user = Users.objects.create(
            username="admin",
            password=make_password("adminpass123"),
            age=25,
            sex="male",
            is_admin=True,
            is_active=True,
        )

        # Create test regular user
        self.regular_user = Users.objects.create(
            username="regular",
            password=make_password("regularpass123"),
            age=25,
            sex="male",
            is_active=True,
        )

        self.client = Client()

        # Valid training parameters with all fields except 'test' set to None
        # Since this is a test
        self.valid_params = {
            "clear_cache": None,
            "force_gpu": None,
            "test": True,
            "db_images_name": None,
            "db_app_name": None,
            "images_table_name": None,
            "app_table_name": None,
            "row_limit": None,
            "start_row": None,
            "test_size": None,
            "random_state": None,
            "input_size": None,
            "num_classes": None,
            "dropout_rate": None,
            "loss_function": None,
            "num_epochs": None,
            "batch_size": None,
            "learning_rate": None,
        }

    def login_admin(self):
        # Helper for admin user login
        response = self.client.post(
            reverse("api-login"),
            data=json.dumps({"username": "admin", "password": "adminpass123"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        token = response.json().get("token")
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"

    def login_regular(self):
        # Helper for regular user login
        response = self.client.post(
            reverse("api-login"),
            data=json.dumps({"username": "regular", "password": "regularpass123"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        token = response.json().get("token")
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"

    def test_post_unauthorized(self):
        # Send req
        response = self.client.post(
            reverse("api-retrain-model"),
            data=json.dumps(self.valid_params),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_post_non_admin(self):
        # Login as regular user via helper
        self.login_regular()

        # Send req
        response = self.client.post(
            reverse("api-retrain-model"),
            data=json.dumps(self.valid_params),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_post_missing_fields(self):
        # Login as admin via helper
        self.login_admin()
        # Delete a param
        invalid_params = self.valid_params.copy()
        del invalid_params["num_classes"]

        # Send req
        response = self.client.post(
            reverse("api-retrain-model"),
            data=json.dumps(invalid_params),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["err"], "Missing fields")

    def test_post_success(self):
        """Test successful training job creation and completion"""
        self.login_admin()

        # Start the training job
        response = self.client.post(
            reverse("api-retrain-model"),
            data=json.dumps(self.valid_params),
            content_type="application/json",
        )

        # Assert status code and jobid message
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("job_id", response_data)

        # Get the job ID
        job_id = response_data["job_id"]

        # Poll the jobs endpoint until the job completes or times out
        poll_interval = 2  # Time between polls in seconds
        start_time = time.time()
        wait_until = start_time + 360  # max 6 mins

        # Continously polling until the job completes or times out
        while time.time() < wait_until:
            # Get all jobs
            jobs_response = self.client.get(reverse("api-retrain-model"))
            self.assertEqual(jobs_response.status_code, 200)

            # Access the jobs array
            jobs = jobs_response.json()["jobs"]
            # Find the job that we started
            current_job = next((job for job in jobs if job["job_id"] == job_id), None)

            # Ensure that the job is found
            self.assertIsNotNone(current_job, "Job not found in jobs list")

            # If it's completed, break out of the loop
            if current_job["status"] == "completed":
                # Test success
                return
            elif current_job["status"] == "failed":
                # If it failed, fail the test
                self.fail(
                    f"Training job failed: {current_job.get('error', 'No error message available')}"
                )

            # Wait before polling to avoid spamming the server
            time.sleep(poll_interval)

        # Fail the job if it takes too long to complete
        self.fail(f"Job did not complete within {max_wait_time} seconds")

        # Miscellaneous permissiong tests

        # Test get jobs endpoint when unauthorized
        def test_get_jobs_unauthorized(self):
            response = self.client.get(reverse("api-retrain-model"))
            self.assertEqual(response.status_code, 401)

        # Test get jobs endpoint when logged in as regular user
        def test_get_jobs_non_admin(self):
            self.login_regular()
            response = self.client.get(reverse("api-retrain-model"))
            self.assertEqual(response.status_code, 401)

        # Test get jobs endpoint when logged in as admin
        def test_get_jobs_success(self):
            self.login_admin()
            response = self.client.get(reverse("api-retrain-model"))
            self.assertEqual(response.status_code, 200)

        # Test delete jobs endpoint when unauthorized
        def test_delete_jobs_unauthorized(self):
            response = self.client.delete(reverse("api-retrain-model"))
            self.assertEqual(response.status_code, 401)

        # Test delete jobs endpoint when logged in as regular user
        def test_delete_jobs_non_admin(self):
            self.login_regular()
            response = self.client.delete(reverse("api-retrain-model"))
            self.assertEqual(response.status_code, 401)

        # Test delete jobs endpoint when logged in as admin
        def test_delete_jobs_success(self):
            self.login_admin()
            response = self.client.delete(reverse("api-retrain-model"))
            self.assertEqual(response.status_code, 204)
