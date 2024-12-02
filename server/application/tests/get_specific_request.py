from django.test import TestCase, Client
from django.urls import reverse
from ..models import Model, Requests, Users


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

        # Create a request for the normal user
        self.user_request = Requests.objects.create(
            created_at=1234567890,
            probability=95,
            image=b"image_data",
            localization="face",
            lesion_type="nv",
            user=self.normal_user,
            model=self.model_version,
        )

        # Create a request for another user
        self.other_user_request = Requests.objects.create(
            created_at=1234567891,
            probability=90,
            image=b"image_data",
            localization="ear",
            lesion_type="mel",
            user=self.other_user,
            model=self.model_version,
        )

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
