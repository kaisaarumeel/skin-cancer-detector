from django.test import TestCase, Client
from django.urls import reverse
from ..models import Model, Requests, Users


class GetRequestsByUsernameTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()

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

        # Create requests
        Requests.objects.create(
            created_at=1234567890,
            probability=95,
            image=b"image_data",
            localization="face",
            lesion_type="nv",
            user=self.test_user,
            model=1,
        )

        Requests.objects.create(
            created_at=1234567891,
            probability=90,
            image=b"image_data",
            localization="ear",
            lesion_type="mel",
            user=self.test_user,
            model=2,
        )

    def test_get_requests_by_username(self):
        """Test retrieving requests by username"""
        self.client.force_login(self.test_user)
        response = self.client.get(reverse("api-get-requests-by-username"))
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertIn("requests", response_data)

        # check the response contains two requests
        requests = response_data["requests"]
        self.assertEqual(len(requests), 2)

    def test_get_requests_by_username_empty(self):
        """Test retrieving empty requests by username"""
        self.client.force_login(self.other_user)
        response = self.client.get(reverse("api-get-requests-by-username"))
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertIn("requests", response_data)

        # check the response contains two requests
        requests = response_data["requests"]
        self.assertEqual(len(requests), 0)

    def test_get_requests_unauthenticated(self):
        """Test retrieving requests without logging in"""
        response = self.client.get(reverse("api-get-requests-by-username"))
        self.assertEqual(response.status_code, 401)
