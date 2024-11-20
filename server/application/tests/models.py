import json
import random
import time
import os

from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Users
from ..models import Model
from unittest.mock import patch


class ModelTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()

        # create 5 test models, where the first one is active
        # other attributes without default values are randomized
        for i in range(5):
            model = Model.objects.create(
                created_at=random.randint(0, int(time.time())),
                version=f"{random.randint(1, 10)}.{random.randint(0, 99)}.{random.randint(0, 99)}",
                weights=os.urandom(128),
                status="active" if i == 0 else "archived",
            )
            if i == 0:
                self.active_model = (
                    model  # save a reference to the active model for test data
                )

        # create a user with admin privileges to test admin-restricted model endpoints
        self.test_user_admin = Users.objects.create(
            username=f"testadmin",
            password=make_password("testpass123"),
            age=random.randint(0, 99),
            sex=random.choice(["male", "female"]),
            is_active=True,
            is_admin=True,
        )

        # test data
        self.invalid_model_id = 9999

    def test_get_active_model_success(self):
        """Test successfully getting currently active model"""
        self.client.force_login(self.test_user_admin)
        response = self.client.get(
            reverse("api-active-model"), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertEqual(response_data["model_id"], self.active_model.model_id)

    def test_get_active_model_no_active_model(self):
        """Test getting active model when none exists in database"""
        self.client.force_login(self.test_user_admin)
        Model.objects.filter(status="active").delete()
        response = self.client.get(
            reverse("api-active-model"), content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)

    def test_get_all_models_success(self):
        """Test successfully getting all models"""
        self.client.force_login(self.test_user_admin)
        response = self.client.get(
            reverse("api-all-models"), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn(
            "models", response_data
        )  # check whether key 'models' exists in response data

    def test_swap_model_success(self):
        """Test successfully swapping active model"""
        self.client.force_login(self.test_user_admin)
        new_model = Model.objects.filter(
            status="archived"
        ).first()  # get the first archived model
        response = self.client.put(
            reverse("api-swap-model", kwargs={"model_id": new_model.model_id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)
        self.assertIn(
            f"Active model swapped to model {new_model.model_id} version {new_model.version}",
            response_data["message"],
        )  # check whether the response contains the correct success message

        new_model.refresh_from_db()
        self.assertEqual(
            new_model.status, "active"
        )  # check that the new model is now active

        other_models = Model.objects.exclude(
            model_id=new_model.model_id
        )  # get all models other than the currently active
        for model in other_models:
            self.assertNotEqual(
                model.status, "active"
            )  # check that all other models are not active

    def test_swap_model_not_found(self):
        """Test swapping model with model_id not in database"""
        self.client.force_login(self.test_user_admin)
        response = self.client.put(
            reverse("api-swap-model", kwargs={"model_id": self.invalid_model_id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
        self.assertEqual(
            response_data["error"], "Model not found."
        )  # check whether the response contains the correct error message

    def test_swap_model_value_error(self):
        """Test swapping model with an invalid model_id value"""
        self.client.force_login(self.test_user_admin)

        # create an exception during the update by providing no model_id
        # django's url resolver raises error because the URL pattern expects a numeric value
        with self.assertRaises(Exception):
            self.client.put(
                reverse("api-swap-model", kwargs={"model_id": None}),
                content_type="application/json",
            )

    # simulate internal server error by mocking Model's save() method, causing an exception
    @patch(
        "application.models.Model.save",
        side_effect=Exception("Forced internal server error"),
    )
    def test_swap_model_internal_server_error(self, mock_save):
        """Test swapping model with a mock internal server error"""
        self.client.force_login(self.test_user_admin)
        new_model = Model.objects.filter(
            status="archived"
        ).first()  # get the first archived model
        response = self.client.put(
            reverse("api-swap-model", kwargs={"model_id": new_model.model_id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)

        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
        self.assertIn(
            "Failed to swap models", response_data["error"]
        )  # check whether the response contains the correct error message
