from django.test import TestCase, Client
from django.urls import reverse
from ..models import Model, Requests, Users
import base64
import os


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

        # Create a model version
        self.model_version = Model.objects.create(
            created_at=1234567890,
            weights=b"test_weights",
            hyperparameters="default",
        )

        self.valid_image_path = os.path.join(
            os.path.dirname(__file__), "test_data", "valid_test_image.jpg"
        )

        self.encoded_image = self.encode_image_to_base64(self.valid_image_path)

        # Create a request for the normal user
        self.user_request = Requests.objects.create(
            created_at=1234567890,
            probability=95,
            image=base64.b64decode(self.encoded_image),
            localization="face",
            lesion_type="nv",
            user=self.normal_user,
            model=self.model_version,
            impact_age=0.1,
            impact_sex=0.2,
            impact_localization=0.3,
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
            model=self.model_version,
            impact_age=0.15,
            impact_sex=0.25,
            impact_localization=0.35,
            heatmap=b"other_dummy_heatmap_data",
        )

        # Create a request for another user with null fields
        self.null_fields_request = Requests.objects.create(
            created_at=1234567892,
            probability=None,
            image=base64.b64decode(self.encoded_image),
            localization="ear",
            lesion_type=None,
            user=self.normal_user,
            model=None,
            impact_age=None,
            impact_sex=None,
            impact_localization=None,
            heatmap=None,
        )

    def encode_image_to_base64(self, file_path):
        """Helper method to encode an image to Base64 and include the data URI prefix"""
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

        self.assertIn("image", response_data["request"])
        self.assertEqual(
            base64.b64decode(response_data["request"]["image"]), self.user_request.image
        )
        self.assertIn("feature_impact", response_data["request"])
        self.assertEqual(len(response_data["request"]["feature_impact"]), 3)
        self.assertIn("pixel_impact", response_data["request"])
        if self.user_request.heatmap:
            self.assertEqual(
                base64.b64decode(response_data["request"]["pixel_impact"]),
                self.user_request.heatmap,
            )
        else:
            self.assertIsNone(response_data["request"]["pixel_impact"])

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
        self.assertEqual(response_data["err"], "access denied")

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
        self.assertEqual(len(response_data["request"]["feature_impact"]), 3)
        for impact in response_data["request"]["feature_impact"]:
            self.assertIsNone(impact["impact"])

        self.assertIn("pixel_impact", response_data["request"])
        self.assertIsNone(response_data["request"]["pixel_impact"])

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
        self.assertEqual(len(response_data["request"]["feature_impact"]), 3)
        for impact in response_data["request"]["feature_impact"]:
            self.assertIn("feature", impact)
            self.assertIn("impact", impact)
            self.assertIsNotNone(impact["feature"])
            self.assertIsNotNone(impact["impact"])

        # Check pixel impact
        self.assertIn("pixel_impact", response_data["request"])
        if self.user_request.heatmap:
            self.assertEqual(
                base64.b64decode(response_data["request"]["pixel_impact"]),
                self.user_request.heatmap,
            )
        else:
            self.assertIsNone(response_data["request"]["pixel_impact"])
