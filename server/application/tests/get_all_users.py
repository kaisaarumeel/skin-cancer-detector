from django.test import TestCase, Client
from django.urls import reverse
from ..models import Users


class GetAllUsersTests(TestCase):
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

        # Create test users using Users.objects.create instead of create_user
        self.user1 = Users.objects.create(
            username="user1",
            password="password123",
            is_admin=True,
            age=30,
            sex="male",
        )

        self.user2 = Users.objects.create(
            username="user2",
            password="password123",
            is_admin=False,
            age=25,
            sex="female",
        )

    def test_get_all_users_success(self):
        """Test retrieving all users successfully"""
        self.client.force_login(self.test_user_admin)
        response = self.client.get(reverse("api-get-all-users"))

        # Verify response status
        self.assertEqual(response.status_code, 200)

        # Parse response data
        response_data = response.json()
        self.assertIn("users", response_data)

        # Validate the number of users returned
        users = response_data["users"]
        self.assertEqual(len(users), 3)

        # Validate user1 data
        user1_data = next(user for user in users if user["username"] == "user1")
        self.assertEqual(user1_data["username"], "user1")
        self.assertEqual(user1_data["is_admin"], True)
        self.assertEqual(user1_data["age"], 30)
        self.assertEqual(user1_data["sex"], "male")

        # Validate user2 data
        user2_data = next(user for user in users if user["username"] == "user2")
        self.assertEqual(user2_data["username"], "user2")
        self.assertEqual(user2_data["is_admin"], False)
        self.assertEqual(user2_data["age"], 25)
        self.assertEqual(user2_data["sex"], "female")

    def test_get_all_users_empty(self):
        """Test retrieving users when no users exist"""
        self.client.force_login(self.test_user_admin)
        # Clear all users
        Users.objects.exclude(username=self.test_user_admin.username).all().delete()

        response = self.client.get(reverse("api-get-all-users"))

        # Verify response status
        self.assertEqual(response.status_code, 200)

        # Parse response data
        response_data = response.json()
        self.assertIn("users", response_data)

        # Validate empty users list
        self.assertEqual(len(response_data["users"]), 1)

    def test_get_all_users_server_error(self):
        """Test handling of server error"""
        self.client.force_login(self.test_user_admin)
        # Simulate an exception by overriding the Users model query
        original_objects = Users.objects

        try:

            class MockObjects:
                def all(self):
                    raise Exception("Simulated server error")

            Users.objects = MockObjects()

            response = self.client.get(reverse("api-get-all-users"))

            # Verify response status
            self.assertEqual(response.status_code, 500)

            # Parse response data
            response_data = response.json()
            self.assertIn("err", response_data)
            self.assertEqual(
                response_data["err"], "Error retrieving users: Simulated server error"
            )

        finally:
            # Restore original Users.objects
            Users.objects = original_objects
