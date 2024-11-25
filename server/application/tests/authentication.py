import json

from django.contrib.auth.hashers import check_password, make_password
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Users


class AuthenticationTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()
        self.test_user = Users.objects.create(
            username="testuser",
            password=make_password("testpass123"),
            age=25,
            sex="male",
            is_active=True,
        )

        self.test_admin_user = Users.objects.create(
            username="admin",
            password=make_password("admin"),
            age=25,
            sex="male",
            is_admin=True,
            is_active=True,
        )

        # Test data
        self.admin_login_data = {
            "username": "admin",
            "password": "admin",
        }
        self.valid_login_data = {"username": "testuser", "password": "testpass123"}
        self.valid_register_data = {
            "username": "newuser",
            "password": "newpass123",
            "age": 30,
            "sex": "female",
        }
        self.valid_password_change = {"new_password": "newpass456"}

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(
            reverse("api-login"),
            json.dumps(self.valid_login_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        invalid_data = {"username": "testuser"}
        response = self.client.post(
            reverse("api-login"),
            json.dumps(invalid_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        invalid_data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(
            reverse("api-login"),
            json.dumps(invalid_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(
            reverse("api-register"),
            json.dumps(self.valid_register_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

    def test_register_missing_fields(self):
        """Test registration with missing fields"""
        invalid_data = {
            "username": "newuser",
            "password": "newpass123",
            "sex": "female",
            # missing age field
        }

        response = self.client.post(
            reverse("api-register"),
            json.dumps(invalid_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_user(self):
        """Test registration with existing username"""
        duplicate_data = self.valid_register_data.copy()
        duplicate_data["username"] = "testuser"

        response = self.client.post(
            reverse("api-register"),
            json.dumps(duplicate_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_logout_success(self):
        """Test successful logout"""
        # First, log in
        self.client.post(
            reverse("api-login"),
            json.dumps(self.valid_login_data),
            content_type="application/json",
        )

        # Now log out
        response = self.client.post(reverse("api-logout"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["msg"], "Successfully logged out")

        # Verify that the session is cleared
        response = self.client.get(reverse("api-is-logged-in"))
        self.assertEqual(response.status_code, 401)

    def test_is_logged_in_authenticated(self):
        """Test if the user is logged in"""
        # Log in first
        self.client.post(
            reverse("api-login"),
            json.dumps(self.valid_login_data),
            content_type="application/json",
        )

        response = self.client.get(reverse("api-is-logged-in"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)["is_logged_in"])

    def test_is_logged_in_unauthenticated(self):
        """Test if the user is not logged in"""
        response = self.client.get(reverse("api-is-logged-in"))
        self.assertEqual(response.status_code, 401)
        self.assertFalse(json.loads(response.content)["is_logged_in"])

    def test_is_admin_authenticated_admin(self):
        """Test if an admin user is correctly identified as an admin"""
        # Log in as the admin user
        login_response = self.client.post(
            reverse("api-login"),
            json.dumps(self.admin_login_data),
            content_type="application/json",
        )
        self.assertEqual(login_response.status_code, 200)  # Ensure login was successful

        # Now check if the logged-in user is identified as an admin
        response = self.client.get(reverse("api-is-admin"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)["is_admin"])

    def test_is_admin_unauthenticated(self):
        """Test if a user who is not logged in is denied access to admin check"""
        response = self.client.get(reverse("api-is-admin"))
        self.assertEqual(response.status_code, 401)
        self.assertFalse(json.loads(response.content)["is_logged_in"])

    def test_change_password_success(self):
        """Test successful password change"""
        # Login first
        self.client.post(
            reverse("api-login"),
            json.dumps(self.valid_login_data),
            content_type="application/json",
        )

        response = self.client.post(
            reverse("api-change-password"),
            json.dumps(self.valid_password_change),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        # Verify password was actually changed
        updated_user = Users.objects.get(username="testuser")
        self.assertTrue(
            check_password(
                self.valid_password_change["new_password"], updated_user.password
            )
        )

    def test_change_password_missing_fields(self):
        """Test password change with missing fields"""
        # Login first
        self.client.post(
            reverse("api-login"),
            json.dumps(self.valid_login_data),
            content_type="application/json",
        )

        response = self.client.post(
            reverse("api-change-password"),
            json.dumps({}),  # Empty data to test missing fields
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("err", json.loads(response.content))

    def test_change_password_unauthenticated(self):
        """Test password change without login"""
        response = self.client.post(
            reverse("api-change-password"),
            json.dumps(self.valid_password_change),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
