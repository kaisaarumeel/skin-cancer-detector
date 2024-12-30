# Contributors:
# * Contributor: <kaisa.arumeel@gmail.com>
import json

from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Users


class DeleteUserTests(TestCase):
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
        self.user_login_data = {"username": "testuser", "password": "testpass123"}

    def login_admin(self):
        """Helper method to log in as the admin"""
        login_response = self.client.post(
            reverse("api-login"),
            json.dumps(self.admin_login_data),
            content_type="application/json",
        )
        self.assertEqual(login_response.status_code, 200)

    def test_delete_user_success(self):
        """Test that an admin user can delete another user"""
        self.login_admin()

        # Ensure user exists before deletion
        self.assertTrue(Users.objects.filter(username="testuser").exists())

        # Perform delete request
        delete_response = self.client.delete(
            reverse("api-delete-user", args=[self.test_user.username]),
            content_type="application/json",
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(
            delete_response.json().get("msg"), "User deleted successfully."
        )

        # Ensure user no longer exists
        self.assertFalse(Users.objects.filter(username="testuser").exists())

    def test_delete_user_not_authenticated(self):
        """Test that unauthenticated users cannot delete a user"""
        delete_response = self.client.delete(
            reverse("api-delete-user", args=[self.test_user.username]),
            content_type="application/json",
        )
        self.assertEqual(delete_response.status_code, 403)
        self.assertEqual(
            delete_response.json().get("err"), "Unauthorized. Admin access required."
        )

    def test_delete_user_as_non_admin(self):
        """Test that non-admin users cannot delete a user"""
        # Log in as a non-admin user
        login_response = self.client.post(
            reverse("api-login"),
            json.dumps(self.user_login_data),
            content_type="application/json",
        )
        self.assertEqual(login_response.status_code, 200)

        delete_response = self.client.delete(
            reverse("api-delete-user", args=[self.test_user.username]),
            content_type="application/json",
        )
        self.assertEqual(delete_response.status_code, 403)
        self.assertEqual(
            delete_response.json().get("err"), "Unauthorized. Admin access required."
        )

    def test_delete_nonexistent_user(self):
        """Test that trying to delete a non-existent user returns a 404"""
        self.login_admin()

        delete_response = self.client.delete(
            reverse("api-delete-user", args=["nonexistentuser"]),
            content_type="application/json",
        )
        self.assertEqual(delete_response.status_code, 404)
        self.assertEqual(delete_response.json().get("err"), "User not found.")

    def test_admin_cannot_delete_themselves(self):
        """Test that an admin cannot delete their own account"""
        self.login_admin()

        delete_response = self.client.delete(
            reverse("api-delete-user", args=[self.test_admin_user.username]),
            content_type="application/json",
        )
        self.assertEqual(delete_response.status_code, 400)
        self.assertEqual(
            delete_response.json().get("err"), "Admin cannot delete themselves."
        )
        # Ensure admin still exists
        self.assertTrue(Users.objects.filter(username="admin").exists())
