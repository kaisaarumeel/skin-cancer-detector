from django.test import TestCase
import numpy as np
import cv2
import os
from ..predictions.preprocess_user_data import preprocess_images


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

    def tearDown(self):
        """Teardown method for cleaning up after tests."""
        pass
