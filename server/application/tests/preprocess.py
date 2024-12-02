from django.test import TestCase
import numpy as np
import cv2
import os
from ..predictions.preprocess_user_data import preprocess_images, extract_images
from unittest.mock import MagicMock

class PreprocessDataTests(TestCase):
    def setUp(self):
        """Setup for tests, called before each test method."""
        super().setUp()
        # Create target input shape
        self.target_input_shape = (224, 224)

        # Test data file paths
        self.valid_image_path = os.path.join(
            os.path.dirname(__file__), "test_data", "valid_test_image.jpg"
        )
        self.valid_image_path2 = os.path.join(
            os.path.dirname(__file__), "test_data", "valid_test_image2.jpeg"
        )
        self.invalid_image_path = os.path.join(
            os.path.dirname(__file__), "test_data", "invalid_test_image_format.gif"
        )

        # Load valid test images into memory
        self.valid_image = cv2.imread(self.valid_image_path)
        self.valid_image2 = cv2.imread(self.valid_image_path2)
        if self.valid_image is None or self.valid_image2 is None:
            raise FileNotFoundError(f"Valid test images not found.")

    def test_preprocess_valid_images(self):
        """Test preprocessing of a list of valid images."""
        try:
            # Preprocess a list of valid images
            result = preprocess_images([self.valid_image, self.valid_image2], self.target_input_shape)

            # Assertions
            self.assertEqual(result.shape, (2, *self.target_input_shape, 3), f"Unexpected shape: {result.shape}")
            self.assertTrue(result.dtype == np.float16, f"Unexpected dtype: {result.dtype}")
            self.assertTrue(
                np.all(result >= -1.0) and np.all(result <= 1.0),
                "Normalization out of range",
            )

        except Exception as e:
            self.fail(f"Valid image preprocessing failed: {str(e)}")

    def test_preprocess_invalid_image(self):
        """Test preprocessing of an invalid image."""
        try:
            # Load invalid image
            invalid_image = cv2.imread(self.invalid_image_path)  
            if invalid_image is None:
                raise ValueError("Invalid test image could not be loaded. Check the file format.")

            preprocess_images([invalid_image], self.target_input_shape)

            # If no exception is raised, fail the test
            self.fail("Preprocessing an invalid image did not raise an error.")

        except Exception as e:
            # An exception is expected for invalid input; ensure it's meaningful
            self.assertIn("could not be loaded", str(e).lower(), f"Unexpected error message: {str(e)}")


    def test_extract_images_valid_jobs(self):
        """Test extraction of images from valid job objects."""
        # Mock job objects with images in their parameters
        job1 = MagicMock()
        job1.parameters = {"image": self.valid_image}
        job2 = MagicMock()
        job2.parameters = {"image": self.valid_image2}

        jobs = [job1, job2]

        # Extract images
        result = extract_images(jobs)

        # Check that the result is a list
        self.assertIsInstance(result, list)

        # Check that the list contains the correct number of images (2)
        self.assertEqual(len(result), 2)

        # Check that the first and second images match the mock images
        np.testing.assert_array_equal(result[0], self.valid_image)
        np.testing.assert_array_equal(result[1], self.valid_image2)

    def test_extract_images_empty_jobs(self):
        """Test extraction from an empty list of jobs."""
        jobs = []

        # Extract images
        result = extract_images(jobs)

        # Ensure that the result is an empty list
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_extract_images_missing_images(self):
        """Test extraction when some jobs have missing images."""
        # Mock job objects with missing image data
        job1 = MagicMock()
        job1.parameters = {"image": self.valid_image}
        job2 = MagicMock()
        job2.parameters = {"image": None}  # Missing image

        jobs = [job1, job2]

        # Extract images
        result = extract_images(jobs)

        # Ensure that the first image is the valid image and the second is None
        np.testing.assert_array_equal(result[0], self.valid_image)
        self.assertIsNone(result[1])

    def test_extract_images_non_image_data(self):
        """Test extraction when the image field contains non-image data."""
        # Mock job objects with non-image data in the image field
        job1 = MagicMock()
        job1.parameters = {"image": "non_image_data"}  # Non-image data
        job2 = MagicMock()
        job2.parameters = {"image": 12345}  # Non-image integer data

        jobs = [job1, job2]

        # Extract images
        result = extract_images(jobs)

        # Ensure that the result contains the non-image data as is
        self.assertEqual(result[0], "non_image_data")
        self.assertEqual(result[1], 12345)

    def test_extract_images_large_number_of_jobs(self):
        """Test extraction with a large number of jobs."""
        # Generate a large number of jobs (e.g., 1000 jobs)
        jobs = []
        for i in range(1000):
            job = MagicMock()
            job.parameters = {"image": np.random.rand(224, 224, 3)}  # Mock image data
            jobs.append(job)

        # Extract images
        result = extract_images(jobs)

        # Check that the result contains 1000 images
        self.assertEqual(len(result), 1000)
        self.assertTrue(all(isinstance(image, np.ndarray) for image in result))  # Ensure each entry is an image array

    def tearDown(self):
        """Teardown method for cleaning up after tests."""
        pass
