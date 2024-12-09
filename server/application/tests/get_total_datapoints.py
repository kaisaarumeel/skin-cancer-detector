from django.test import TestCase, Client
from django.urls import reverse
from ..models import Data, Users


class GetTotalDataPointsTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()

        # Create an admin user for testing
        self.test_user_admin = Users.objects.create(
            username="testadmin",
            password="testadminpassword",
            age=30,
            sex="male",
            is_active=True,
            is_admin=True,
        )

        # Create some sample data points
        # Create some sample data points
        Data.objects.create(
            image_id="datapoint1",
            created_at=1700000000,
            image=b"dummy_binary_data_1",
            age=45,
            sex="male",
            localization="face",
            lesion_type="mel",
        )
        Data.objects.create(
            image_id="datapoint2",
            created_at=1700000001,
            image=b"dummy_binary_data_2",
            age=30,
            sex="female",
            localization="neck",
            lesion_type="nv",
        )
        Data.objects.create(
            image_id="datapoint3",
            created_at=1700000002,
            image=b"dummy_binary_data_3",
            age=60,
            sex="male",
            localization="back",
            lesion_type="bcc",
        )
        Data.objects.create(
            image_id="datapoint4",
            created_at=1700000003,
            image=b"dummy_binary_data_4",
            age=25,
            sex="female",
            localization="hand",
            lesion_type="akiec",
        )
        Data.objects.create(
            image_id="datapoint5",
            created_at=1700000004,
            image=b"dummy_binary_data_5",
            age=50,
            sex="male",
            localization="abdomen",
            lesion_type="df",
        )

    def test_get_total_data_points(self):
        """Test retrieving total data points"""
        # Log in as admin
        self.client.force_login(self.test_user_admin)

        # Make GET request to the endpoint
        response = self.client.get(reverse("api-get-total-data-points"))
        self.assertEqual(response.status_code, 200)

        # Parse response data
        response_data = response.json()

        # Validate total, test, and train data points
        self.assertIn("total_data_points", response_data)
        self.assertIn("test_total", response_data)
        self.assertIn("train_total", response_data)

        # Verify counts
        total_data_points = response_data["total_data_points"]
        test_total = response_data["test_total"]
        train_total = response_data["train_total"]

        self.assertEqual(total_data_points, 5)  # Total data points = 5
        self.assertEqual(test_total, 1)  # Test = 20% of 5 (rounded down)
        self.assertEqual(train_total, 4)  # Train = Total - Test

    def test_unauthorized_access(self):
        """Test access without admin privileges"""
        # Make GET request without logging in
        response = self.client.get(reverse("api-get-total-data-points"))
        self.assertEqual(response.status_code, 401)  # Forbidden for unauthorized users
