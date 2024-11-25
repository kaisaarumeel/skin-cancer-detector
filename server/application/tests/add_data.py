import random
import time
import os

from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Data
from ..models import Users


class AddDataTests(TestCase):

    databases = {"default", "db_images"}

    def setUp(self):
        """Set up test data and client"""
        self.client = Client()

        # create a user with admin privileges to test admin-restricted model endpoints
        self.test_user_admin = Users.objects.create(
            username=f"testadmin",
            password=make_password("testpass123"),
            age=random.randint(0, 99),
            sex=random.choice(["male", "female"]),
            is_active=True,
            is_admin=True,
        )

        # create one existing entry
        Data.objects.using("db_images").create(
            image_id="image_id",
            created_at=int(time.time()),
            image=os.urandom(128),
            age=random.randint(0, 99),
            sex=random.choice(["male", "female"]),
            localization="foot",
            lesion_type="mel",
        )

        self.default_db_size = 1
        self.test_data_size = 5
        self.data_path_valid = os.path.join(
            os.path.dirname(__file__), "test_data", "new_data_valid.zip"
        )
        self.data_path_duplicate = os.path.join(
            os.path.dirname(__file__), "test_data", "new_data_duplicate.zip"
        )
        self.data_path_invalid_extension = os.path.join(
            os.path.dirname(__file__), "test_data", "new_data_invalid_extension.zip"
        )
        self.data_path_missing_image = os.path.join(
            os.path.dirname(__file__), "test_data", "new_data_missing_image.zip"
        )
        self.data_path_corrupted = os.path.join(
            os.path.dirname(__file__), "test_data", "new_data_corrupted.zip"
        )
        self.data_path_not_zip = os.path.join(
            os.path.dirname(__file__), "test_data", "new_data_not_zip.rar"
        )

    def test_add_data_success_db_empty(self):
        """Test successfully adding new training data to empty db"""
        self.client.force_login(self.test_user_admin)
        Data.objects.using("db_images").all().delete()

        # open zip file in binary mode
        with open(self.data_path_valid, "rb") as f:
            response = self.client.post(
                reverse("add-data"),
                {"file": f},
                format="multipart",
            )

        # verify response
        self.assertEqual(response.status_code, 200)

        # check database for added entries
        db_size = Data.objects.using("db_images").count()
        self.assertEqual(db_size, self.test_data_size)

    def test_add_data_success_db_not_empty(self):
        """Test successfully adding new training data to non-empty db"""
        self.client.force_login(self.test_user_admin)

        # open zip file in binary mode
        with open(self.data_path_valid, "rb") as f:
            response = self.client.post(
                reverse("add-data"),
                {"file": f},
                format="multipart",
            )

        # verify response
        self.assertEqual(response.status_code, 200)

        # check database for added entries
        db_size = Data.objects.using("db_images").count()
        self.assertEqual(db_size, (self.test_data_size + self.default_db_size))

    def test_add_data_duplicate(self):
        """Test adding training data containing images already in db"""
        self.client.force_login(self.test_user_admin)

        # open zip file in binary mode
        with open(self.data_path_duplicate, "rb") as f:
            response = self.client.post(
                reverse("add-data"),
                {"file": f},
                format="multipart",
            )

        # verify response
        self.assertEqual(response.status_code, 200)

        # check database for added entries
        # duplicate dataset contains 1 valid and 1 duplicate image
        db_size = Data.objects.using("db_images").count()
        self.assertEqual(db_size, (self.default_db_size + 1))

    def test_add_data_invalid_image_extension(self):
        """Test adding training data containing invalid image extension"""
        self.client.force_login(self.test_user_admin)

        # open zip file in binary mode
        with open(self.data_path_invalid_extension, "rb") as f:
            response = self.client.post(
                reverse("add-data"),
                {"file": f},
                format="multipart",
            )

        # verify response
        self.assertEqual(response.status_code, 200)

        # check database for added entries
        # dataset contains 1 valid and 1 invalid image
        db_size = Data.objects.using("db_images").count()
        self.assertEqual(db_size, (self.default_db_size + 1))

    def test_add_data_missing_image(self):
        """Test adding training data where missing image is in metadata"""
        self.client.force_login(self.test_user_admin)

        # open zip file in binary mode
        with open(self.data_path_missing_image, "rb") as f:
            response = self.client.post(
                reverse("add-data"),
                {"file": f},
                format="multipart",
            )

        # verify response
        self.assertEqual(response.status_code, 200)

        # check database for added entries
        # dataset contains 1 valid and 1 missing image
        db_size = Data.objects.using("db_images").count()
        self.assertEqual(db_size, (self.default_db_size + 1))

    def test_add_data_corrupted(self):
        """Test adding invalid zip file"""
        self.client.force_login(self.test_user_admin)

        # open zip file in binary mode
        with open(self.data_path_corrupted, "rb") as f:
            response = self.client.post(
                reverse("add-data"),
                {"file": f},
                format="multipart",
            )

        # verify response
        self.assertEqual(response.status_code, 400)

        # check no new entries in database
        db_size = Data.objects.using("db_images").count()
        self.assertEqual(db_size, self.default_db_size)

    def test_add_data_not_zip(self):
        """Test adding a non-zip file"""
        self.client.force_login(self.test_user_admin)

        # open zip file in binary mode
        with open(self.data_path_not_zip, "rb") as f:
            response = self.client.post(
                reverse("add-data"),
                {"file": f},
                format="multipart",
            )

        # verify response
        self.assertEqual(response.status_code, 400)

        # check no new entries in database
        db_size = Data.objects.using("db_images").count()
        self.assertEqual(db_size, self.default_db_size)
