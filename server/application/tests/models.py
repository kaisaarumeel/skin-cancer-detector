import json
import random
import time
import os

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Users
from ..models import Model
from ..models import ActiveModel
from unittest.mock import patch


class ModelTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()

        for i in range(3):
            model = Model.objects.create(
                created_at=random.randint(0, int(time.time())),
                weights=os.urandom(128),
                hyperparameters="insert string to be parsed to JSON",
            )

        # set the last model added to db to be active model
        self.active_model = ActiveModel.objects.create(
            model=model, updated_at=int(time.time())
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
        self.invalid_version = 9999

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

    def test_get_active_model_success(self):
        """Test successfully getting currently active model"""
        self.client.force_login(self.test_user_admin)
        response = self.client.get(
            reverse("api-active-model"), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertEqual(response_data["version"], self.active_model.model.version)

    def test_swap_model_success(self):
        """Test successfully swapping active model"""
        self.client.force_login(self.test_user_admin)
        new_model = Model.objects.first()  # get the first inactive model
        response = self.client.post(
            reverse("api-swap-model", kwargs={"version": new_model.version}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)
        self.assertIn(
            f"Active model changed to version {new_model.version}",
            response_data["message"],
        )  # check whether the response contains the correct success message

        # check that the ActiveModel table shows correct active model
        active_model = ActiveModel.objects.first()
        self.assertIsNotNone(active_model)  # check that a row exists
        self.assertEqual(
            ActiveModel.objects.count(), 1
        )  # check that ONLY one row exists
        self.assertEqual(
            active_model.model, new_model
        )  # check that it points to the correct model

    def test_swap_model_with_itself(self):
        """Test swapping active model with already active model"""
        self.client.force_login(self.test_user_admin)
        new_model = ActiveModel.objects.first().model  # get the active model
        response = self.client.post(
            reverse("api-swap-model", kwargs={"version": new_model.version}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)
        self.assertIn(
            f"Active model changed to version {new_model.version}",
            response_data["message"],
        )  # check whether the response contains the correct success message

        # check that the ActiveModel table shows correct active model
        active_model = ActiveModel.objects.first()
        self.assertIsNotNone(active_model)  # check that a row exists
        self.assertEqual(
            ActiveModel.objects.count(), 1
        )  # check that ONLY one row exists
        self.assertEqual(
            active_model.model, new_model
        )  # check that it points to the correct model

    def test_swap_model_not_found(self):
        """Test swapping model with version not in database"""
        self.client.force_login(self.test_user_admin)
        response = self.client.post(
            reverse("api-swap-model", kwargs={"version": self.invalid_version}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

        response_data = json.loads(response.content)
        self.assertIn("err", response_data)
        self.assertEqual(
            response_data["err"], "Model not found"
        )  # check whether the response contains the correct error message

    def test_swap_model_value_error(self):
        """Test swapping model with an invalid version value"""
        self.client.force_login(self.test_user_admin)

        # create an exception during the update by providing no version
        # django's url resolver raises error because the URL pattern expects a numeric value
        with self.assertRaises(Exception):
            self.client.post(
                reverse("api-swap-model", kwargs={"version": None}),
                content_type="application/json",
            )

    # simulate internal server error by mocking Model's save() method, causing an exception
    @patch(
        "application.models.ActiveModel.save",
        side_effect=Exception("Forced internal server error"),
    )
    def test_swap_model_internal_server_error(self, mock_save):
        """Test swapping model with a mock internal server error"""
        self.client.force_login(self.test_user_admin)
        new_model = Model.objects.first()  # get the first archived model
        response = self.client.post(
            reverse("api-swap-model", kwargs={"version": new_model.version}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)

        response_data = json.loads(response.content)
        self.assertIn("err", response_data)
        self.assertIn(
            "Failed to swap models", response_data["err"]
        )  # check whether the response contains the correct error message

    def test_get_active_model_no_active_model(self):
        """Test getting active model when none exists in database"""
        self.client.force_login(self.test_user_admin)
        ActiveModel.objects.all().delete()  # ensure active model is deleted
        response = self.client.get(
            reverse("api-active-model"), content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)

        response_data = json.loads(response.content)
        self.assertIn("err", response_data)
        self.assertEqual(response_data["err"], "No active model found")

    def test_swap_model_if_none_exists(self):
        """Test setting an active model if none already exist"""
        self.client.force_login(self.test_user_admin)
        ActiveModel.objects.all().delete()  # ensure active model is deleted
        new_model = Model.objects.first()  # get the first inactive model
        response = self.client.post(
            reverse("api-swap-model", kwargs={"version": new_model.version}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)
        self.assertIn(
            f"Active model changed to version {new_model.version}",
            response_data["message"],
        )  # check whether the response contains the correct success message

        # check that the ActiveModel table shows correct active model
        active_model = ActiveModel.objects.first()
        self.assertIsNotNone(active_model)  # check that a row exists
        self.assertEqual(
            ActiveModel.objects.count(), 1
        )  # check that ONLY one row exists
        self.assertEqual(
            active_model.model, new_model
        )  # check that it points to the correct model
    
    def test_delete_model_success(self):
        """test successfully deleting a model"""
        self.client.force_login(self.test_user_admin)
        model = Model.objects.first()  # get the first model
        response = self.client.delete(
            reverse("api-delete-model", kwargs={"version": model.version}))
        
        self.assertEqual(response.status_code, 204)
        self.assertRaises(ObjectDoesNotExist, Model.objects.get, version=model.version)

    def test_delete_model_does_not_exist(self):
        """test deleting a model that doesn't exist"""
        self.client.force_login(self.test_user_admin)
        response = self.client.delete(
            reverse("api-delete-model", kwargs={"version": self.invalid_version}))
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_active_model_cascade(self):
        """test deleting the active model and cascading to the ActiveModel table"""
        self.client.force_login(self.test_user_admin)
        response = self.client.delete(
            reverse("api-delete-model", kwargs={"version": self.active_model.model.version}))
        
        self.assertEqual(response.status_code, 204)
        self.assertRaises(ObjectDoesNotExist, ActiveModel.objects.get, model=self.active_model.model)

