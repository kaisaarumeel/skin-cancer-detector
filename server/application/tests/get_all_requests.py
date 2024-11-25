from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Model, Requests, Users


class GetAllRequestsTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()

        # create a user with admin privileges to test admin-restricted model endpoints
        self.test_user_admin = Users.objects.create(
            username="testadmin",
            password="testadminpassword",
            age=30,
            sex="male",
            is_active=True,
            is_admin=True,
        )

        # Create a test user
        self.test_user = Users.objects.create(
            username="testuser",
            password="testpassword",
            age=25,
            sex="male",
            is_active=True,
        )

        # Create another test user
        self.other_user = Users.objects.create(
            username="otheruser",
            password="testpassword",
            age=30,
            sex="female",
            is_active=True,
        )

        # Create a model (auto-generated version)
        self.model_version = Model.objects.create(
            created_at=1234567890,
            weights=b"test_weights",
            hyperparameters="default",
        )

        # Create requests
        Requests.objects.create(
            created_at=1234567890,
            probability=95,
            image=b"image_data",
            localization="face",
            lesion_type="nv",
            user=self.test_user,
            model=self.model_version,
        )

        Requests.objects.create(
            created_at=1234567891,
            probability=85,
            image=b"image_data",
            localization="arm",
            lesion_type="mel",
            user=self.other_user,
            model=self.model_version,
        )

    def test_get_all_requests(self):
        """Test retrieving all requests"""
        self.client.force_login(self.test_user_admin)
        response = self.client.get(reverse("api-get-all-requests"))
        self.assertEqual(response.status_code, 200)

        # Parse response data
        response_data = response.json()
        self.assertIn("requests", response_data)

        # Validate the response contains two requests
        requests = response_data["requests"]
        self.assertEqual(len(requests), 2)
