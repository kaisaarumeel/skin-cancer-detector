from django.test import TestCase, Client
from django.urls import reverse
from ..models import Model, Requests, Users
import base64
import os
import json


class GetSpecificRequestTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()

        # Create a test admin user
        self.admin_user = Users.objects.create(
            username="adminuser",
            password="testpassword",
            is_admin=True,
            age=30,
            sex="male",
            is_active=True,
        )

        # Create a normal user
        self.normal_user = Users.objects.create(
            username="normaluser",
            password="testpassword",
            is_admin=False,
            age=25,
            sex="female",
            is_active=True,
        )

        # Create another normal user
        self.other_user = Users.objects.create(
            username="otheruser",
            password="testpassword",
            is_admin=False,
            age=28,
            sex="male",
            is_active=True,
        )

        self.valid_image_path = os.path.join(
            os.path.dirname(__file__), "test_data", "valid_test_image.jpg"
        )

        self.encoded_image = self.encode_image_to_base64(self.valid_image_path)

        # Sample feature impact JSON
        self.feature_impact_json = json.dumps(
            {"image": 45.5, "age": 15.2, "location": 39.3}
        )

        # Create a request for the normal user
        self.user_request = Requests.objects.create(
            created_at=1234567890,
            probability=95,
            image=base64.b64decode(self.encoded_image),
            localization="face",
            lesion_type="nv",
            user=self.normal_user,
            model=1,
            feature_impact=self.feature_impact_json,
            heatmap=b"dummy_heatmap_data",
        )

        # Create a request for another user
        self.other_user_request = Requests.objects.create(
            created_at=1234567891,
            probability=90,
            image=base64.b64decode(self.encoded_image),
            localization="ear",
            lesion_type="mel",
            user=self.other_user,
            model=2,
            feature_impact=self.feature_impact_json,
            heatmap=b"other_dummy_heatmap_data",
        )

        # Create a request for another user with null fields
        self.null_fields_request = Requests.objects.create(
            created_at=1234567892,
            probability=None,
            image=base64.b64decode(self.encoded_image),
            localization="ear",  # Using choice key
            lesion_type=None,
            user=self.normal_user,
            model=None,
            feature_impact=None,
            heatmap=None,
        )

    def encode_image_to_base64(self, file_path):
        """Helper method to encode an image to Base64"""
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def test_normal_user_access_own_request(self):
        """Test if a normal user can access their own request"""
        self.client.force_login(self.normal_user)
        response = self.client.get(
            reverse("api-get-specific-request", args=[self.user_request.request_id])
        )
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertIn("request", response_data)
        self.assertEqual(
            response_data["request"]["request_id"], self.user_request.request_id
        )
        self.assertEqual(response_data["request"]["user"], self.normal_user.username)

        # Check image
        self.assertIn("image", response_data["request"])
        self.assertEqual(
            base64.b64decode(response_data["request"]["image"]), self.user_request.image
        )

        # Check impacts
        self.assertIn("feature_impact", response_data["request"])
        feature_impact = json.loads(response_data["request"]["feature_impact"])
        self.assertIsInstance(feature_impact, dict)
        self.assertIn("image", feature_impact)

        # Check heatmap
        self.assertIn("pixel_impact_visualized", response_data["request"])
        if self.user_request.heatmap:
            self.assertEqual(
                base64.b64decode(response_data["request"]["pixel_impact_visualized"]),
                self.user_request.heatmap,
            )
        else:
            self.assertIsNone(response_data["request"]["pixel_impact_visualized"])

    def test_admin_access_any_user_request(self):
        """Test if an admin can access any user's request"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse(
                "api-get-specific-request", args=[self.other_user_request.request_id]
            )
        )
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertIn("request", response_data)
        self.assertEqual(
            response_data["request"]["request_id"], self.other_user_request.request_id
        )
        self.assertEqual(response_data["request"]["user"], self.other_user.username)

    def test_normal_user_access_other_user_request(self):
        """Test if a normal user tries to access another user's request"""
        self.client.force_login(self.normal_user)
        response = self.client.get(
            reverse(
                "api-get-specific-request", args=[self.other_user_request.request_id]
            )
        )
        self.assertEqual(response.status_code, 403)

        response_data = response.json()
        self.assertIn("err", response_data)
        self.assertEqual(response_data["err"], "Access denied.")

    def test_unauthorized_access(self):
        """Test if an unauthorized user tries to access the endpoint"""
        response = self.client.get(
            reverse("api-get-specific-request", args=[self.user_request.request_id])
        )
        self.assertEqual(response.status_code, 401)

        response_data = response.json()
        self.assertIn("err", response_data)
        self.assertEqual(response_data["err"], "Unauthorized")

    def test_request_with_null_fields(self):
        """Test if the endpoint handles a request with null fields correctly"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse(
                "api-get-specific-request", args=[self.null_fields_request.request_id]
            )
        )
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertIn("request", response_data)

        # Ensure the null fields are returned as None
        self.assertIsNone(response_data["request"]["probability"])
        self.assertIsNone(response_data["request"]["model_version"])
        self.assertIsNone(response_data["request"]["lesion_type"])
        self.assertIn("feature_impact", response_data["request"])
        self.assertIsNone(response_data["request"]["feature_impact"])
        self.assertIsNone(response_data["request"]["pixel_impact_visualized"])

    def test_feature_and_pixel_impact(self):
        """Test if feature impacts and pixel impact are returned correctly"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse("api-get-specific-request", args=[self.user_request.request_id])
        )
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertIn("request", response_data)

        # Check feature impact
        self.assertIn("feature_impact", response_data["request"])
        feature_impact = json.loads(response_data["request"]["feature_impact"])
        self.assertIsInstance(feature_impact, dict)
        self.assertIn("image", feature_impact)
        self.assertIsInstance(feature_impact["image"], float)

        # Check pixel impact
        self.assertIn("pixel_impact_visualized", response_data["request"])
        if self.user_request.heatmap:
            self.assertEqual(
                base64.b64decode(response_data["request"]["pixel_impact_visualized"]),
                self.user_request.heatmap,
            )
        else:
            self.assertIsNone(response_data["request"]["pixel_impact_visualized"])
