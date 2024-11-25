import os
import json
import base64
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

    def encode_image_to_base64(self, file_path):
        """Helper method to encode image to Base64"""
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def test_upload_photo_success(self):
        """Test successful photo upload"""
        self.client.force_login(self.test_user)

        # Prepare JSON data and valid Base64 image
        json_data = {
            "localization": "face",
            "lesion_type": "nv",
            "image": self.encode_image_to_base64(self.valid_image_path),
        }
        response = self.client.post(
            reverse("api-upload-photo"),
            json.dumps(json_data),
            content_type="application/json",
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
            json.dumps(json_data),
            content_type="application/json",
        )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("No image file provided", response.json()["err"])

    def test_upload_photo_invalid_json(self):
        """Test upload with invalid JSON"""
        self.client.force_login(self.test_user)

        # Prepare invalid JSON data
        invalid_json = "invalid_json"
        response = self.client.post(
            reverse("api-upload-photo"),
            invalid_json,
            content_type="application/json",
        )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid JSON format", response.json()["err"])

    def test_upload_photo_missing_json(self):
        """Test upload with missing JSON data"""
        self.client.force_login(self.test_user)

        # Send an empty body
        response = self.client.post(
            reverse("api-upload-photo"),
            content_type="application/json",
        )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("No JSON data provided", response.json()["err"])

    def test_upload_photo_missing_required_json_fields(self):
        """Test upload with JSON missing required fields"""
        self.client.force_login(self.test_user)

        # Prepare incomplete JSON data
        incomplete_json = {
            "localization": "face"
        }  # Missing 'lesion_type' and 'image'
        response = self.client.post(
            reverse("api-upload-photo"),
            json.dumps(incomplete_json),
            content_type="application/json",
        )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing or empty required JSON fields", response.json()["err"])
