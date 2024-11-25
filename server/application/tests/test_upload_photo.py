import os
import json
from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Users


class UploadPhotoTests(TestCase):
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

        # Test file paths
        self.valid_image_path = os.path.join(
            os.path.dirname(__file__), "test_data", "valid_test_image.jpg"
        )
        self.invalid_image_path = os.path.join(
            os.path.dirname(__file__), "test_data", "invalid_test_image_format.pdf"
        )

    def test_upload_photo_success(self):
        """Test successful photo upload"""
        self.client.force_login(self.test_user)

        # Prepare JSON data and valid image file
        json_data = {"localization": "face", "lesion_type": "nv"}
        with open(self.valid_image_path, "rb") as img_file:
            response = self.client.post(
                reverse("api-upload-photo"),
                {
                    "image": img_file,
                    "data": json.dumps(json_data),
                },
                format="multipart",
            )

        # Verify response
        self.assertEqual(response.status_code, 201)
        self.assertIn("Image uploaded successfully!", response.json()["msg"])

    def test_upload_photo_missing_image(self):
        """Test upload with missing image"""
        self.client.force_login(self.test_user)

        # Prepare only JSON data
        json_data = {"localization": "face", "lesion_type": "nv"}
        response = self.client.post(
            reverse("api-upload-photo"),
            {
                "data": json.dumps(json_data),
            },
            format="multipart",
        )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("No image file provided", response.json()["err"])

    def test_upload_photo_invalid_json(self):
        """Test upload with invalid JSON"""
        self.client.force_login(self.test_user)

        # Prepare invalid JSON data and valid image file
        invalid_json = "invalid_json"
        with open(self.valid_image_path, "rb") as img_file:
            response = self.client.post(
                reverse("api-upload-photo"),
                {
                    "image": img_file,
                    "data": invalid_json,
                },
                format="multipart",
            )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid JSON format", response.json()["err"])

    def test_upload_photo_missing_json(self):
        """Test upload with missing JSON data"""
        self.client.force_login(self.test_user)

        # Prepare only image file
        with open(self.valid_image_path, "rb") as img_file:
            response = self.client.post(
                reverse("api-upload-photo"),
                {
                    "image": img_file,
                },
                format="multipart",
            )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("No JSON data provided", response.json()["err"])

    def test_upload_photo_missing_required_json_fields(self):
        """Test upload with JSON missing required fields"""
        self.client.force_login(self.test_user)

        # Prepare incomplete JSON data and valid image file
        incomplete_json = {"localization": "face"}  # Missing 'lesion_type'
        with open(self.valid_image_path, "rb") as img_file:
            response = self.client.post(
                reverse("api-upload-photo"),
                {
                    "image": img_file,
                    "data": json.dumps(incomplete_json),
                },
                format="multipart",
            )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing or empty required JSON fields", response.json()["err"])
