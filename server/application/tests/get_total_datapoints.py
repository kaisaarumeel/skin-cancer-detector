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
        Data.objects.create(name="datapoint1", value=10)
        Data.objects.create(name="datapoint2", value=20)
        Data.objects.create(name="datapoint3", value=30)
        Data.objects.create(name="datapoint4", value=40)
        Data.objects.create(name="datapoint5", value=50)

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
        self.assertEqual(test_total, 1)        # Test = 20% of 5 (rounded down)
        self.assertEqual(train_total, 4)       # Train = Total - Test

    def test_unauthorized_access(self):
        """Test access without admin privileges"""
        # Make GET request without logging in
        response = self.client.get(reverse("api-get-total-data-points"))
        self.assertEqual(response.status_code, 401)  # Forbidden for unauthorized users
