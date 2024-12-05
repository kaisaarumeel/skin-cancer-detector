import os
import json
import base64
import time
import numpy as np
from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Users
from unittest.mock import patch
from ..predictions.queue_manager import QueueManager

class CreateRequestTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()

        # Creating a test user
        self.test_user = Users.objects.create(
            username="testuser",
            password=make_password("testpass123"),
            age=25,
            sex="male",
            is_active=True,
        )

        # Test data file paths
        self.valid_image_path = os.path.join(
            os.path.dirname(__file__), "test_data", "valid_test_image.jpg"
        )
        self.invalid_image_path = os.path.join(
            os.path.dirname(__file__), "test_data", "invalid_test_image_format.gif"
        )

    def encode_image_to_base64(self, file_path):
        """Helper method to encode an image to Base64 and include the data URI prefix"""
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    ################################## INTEGRATION TESTS ##################################

    def test_create_request_success(self):
        """Test successful photo upload"""
        self.client.force_login(self.test_user)

        data = {
            "localization": "face",
            "image": self.encode_image_to_base64(self.valid_image_path),
        }
        response = self.client.post(
            reverse("api-create-request"),
            json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["msg"], "Request created successfully! Results pending."
        )

    def test_create_request_creates_valid_job(self):
        """Test that a properly formed Job is created and added to the queue when the endpoint is called"""
        self.client.force_login(self.test_user)

        data = {
            "localization": "face",
            "image": self.encode_image_to_base64(self.valid_image_path),
        }

        # Patch is used to intercept put() calls to the global queue so we can mock the result
        with patch("application.views.create_request.PREDICTION_JOBS.put") as mock_put:

            # Call the endpoint and assert response is successful
            response = self.client.post(
                reverse("api-create-request"),
                json.dumps(data),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                response.json()["msg"], "Request created successfully! Results pending."
            )

            # Verify that the Job was correctly added to the Job queue
            mock_put.assert_called_once()

            # Access the created Job object
            # https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.call_args
            created_job = mock_put.call_args[0][0]

            # Validate the Job object fields
            self.assertAlmostEqual(
                created_job.start_time, int(time.time()), delta=5
            )  # delta sets a limit for the difference
            self.assertEqual(
                created_job.parameters["request_id"], response.json()["request_id"]
            )
            self.assertEqual(created_job.parameters["age"], self.test_user.age)
            self.assertEqual(created_job.parameters["sex"], self.test_user.sex)
            self.assertEqual(
                created_job.parameters["localization"], data["localization"]
            )
            self.assertIsInstance(created_job.parameters["image"], np.ndarray)

    def test_create_request_missing_image(self):
        """Test upload with missing image"""
        self.client.force_login(self.test_user)

        data = {"localization": "face"}
        response = self.client.post(
            reverse("api-create-request"),
            json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["err"], "No image file provided")

    def test_create_request_missing_json(self):
        """Test upload with missing JSON data"""
        self.client.force_login(self.test_user)

        # Send an empty body
        response = self.client.post(
            reverse("api-create-request"),
            content_type="application/json",
        )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("No JSON data provided", response.json()["err"])

    def test_create_request_missing_localization(self):
        """Test upload with JSON missing required 'localization' field"""
        self.client.force_login(self.test_user)

        data = {"image": self.encode_image_to_base64(self.valid_image_path)}
        response = self.client.post(
            reverse("api-create-request"),
            json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["err"], "Missing or empty required field: 'localization'"
        )

    def test_create_request_invalid_localization(self):
        """Test upload with an invalid localization value"""
        self.client.force_login(self.test_user)

        data = {
            "localization": "invalid_location",
            "image": self.encode_image_to_base64(self.valid_image_path),
        }
        response = self.client.post(
            reverse("api-create-request"),
            json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["err"], "Invalid localization value.")

    def test_create_request_invalid_base64_image(self):
        """Test upload with invalid Base64 image format"""
        self.client.force_login(self.test_user)

        data = {
            "localization": "face",
            "image": "invalid_base64_string",
        }
        response = self.client.post(
            reverse("api-create-request"),
            json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid Base64", response.json()["err"])

    def test_create_request_unsupported_format(self):
        """Test upload with unsupported file format"""
        self.client.force_login(self.test_user)

        data = {
            "localization": "face",
            "image": self.encode_image_to_base64(self.invalid_image_path),
        }
        response = self.client.post(
            reverse("api-create-request"),
            json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported image format", response.json()["err"])
