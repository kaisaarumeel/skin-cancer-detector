# Contributors:
# * Contributor: <kaisa.arumeel@gmail.com>
# * Contributor: <elindstr@student.chalmers.se>
# * Contributor: <alexandersafstrom@proton.me>
from django.test import TestCase
import numpy as np
import cv2
import os
from unittest.mock import MagicMock
from sklearn.preprocessing import StandardScaler, LabelEncoder
from ..models import Requests
from ..predictions.prediction_manager import get_model_input_shape
from ..predictions.preprocess_user_data import (
    preprocess_images,
    extract_images,
    extract_tabular_features,
)


class PreprocessDataTests(TestCase):
    def setUp(self):
        """Setup for tests, called before each test method."""
        super().setUp()

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
            result = preprocess_images(
                [self.valid_image, self.valid_image2], self.target_input_shape
            )

            # We should have two images with 224,224 and 3 channels
            # because it is an RGB image
            self.assertEqual(
                result.shape,
                (2, *self.target_input_shape, 3),
                f"Unexpected shape: {result.shape}",
            )

            # We should have the minimal float16 dtype
            self.assertTrue(
                result.dtype == np.float16, f"Unexpected dtype: {result.dtype}"
            )

            # The images need to be within a valid range
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
                raise ValueError(
                    "Invalid test image could not be loaded. Check the file format."
                )

            # Attempt to preprocess the invalid image
            preprocess_images([invalid_image], self.target_input_shape)

            # If no exception is raised, fail the test
            self.fail("Preprocessing an invalid image did not raise an error.")

        except Exception as e:
            # An exception is expected for invalid input; ensure it's meaningful
            self.assertIn(
                "could not be loaded",
                str(e).lower(),
                f"Unexpected error message: {str(e)}",
            )

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
        result = extract_images(jobs)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_extract_images_large_number_of_jobs(self):
        """Test extraction with a large number of jobs."""
        jobs = []
        for i in range(1000):
            job = MagicMock()
            job.parameters = {"image": np.random.rand(224, 224, 3)}
            jobs.append(job)

        result = extract_images(jobs)
        self.assertEqual(len(result), 1000)
        self.assertTrue(all(isinstance(image, np.ndarray) for image in result))

    def test_get_model_input_shape(self):
        """Test that the height and width are correctly extracted from the model input shape."""
        mock_model = MagicMock()
        mock_model.input_shape = [(None, 64, 64, 3)]
        extracted_height, extracted_width = get_model_input_shape(mock_model)
        self.assertEqual(extracted_height, 64)
        self.assertEqual(extracted_width, 64)

    def test_extract_tabular_features_standardized(self):
        """Test the scaling of standardized features."""
        # Create mock jobs with consistent data
        jobs = [
            MagicMock(parameters={"age": 30, "localization": "ear", "sex": "male"}),
            MagicMock(parameters={"age": 50, "localization": "face", "sex": "female"}),
        ]

        # Create and fit scaler with known data
        scaler = StandardScaler()
        X = np.array([[30, 0, 1], [50, 1, 0]])  # age, location encoded, sex encoded
        scaler.fit(X)

        # Create encoder with known mapping
        encoder = LabelEncoder()
        encoder.fit(["ear", "face"])

        # Get features
        result, feature_names = extract_tabular_features(jobs, scaler, encoder)

        # Calculate expected scaled values
        expected = scaler.transform(X)

        # Compare arrays
        np.testing.assert_array_almost_equal(result, expected, decimal=6)
        self.assertEqual(feature_names, ["age", "localization", "sex"])

    def test_extract_tabular_features_encoding(self):
        """Test the encoding of localization labels."""
        # Get all possible localizations from model
        localizations = [loc[0] for loc in Requests.LOCALIZATION_CHOICES]

        # Create mock jobs with different localizations
        jobs = []
        for loc in localizations[:2]:  # Use just first two for simplicity
            job = MagicMock()
            job.parameters = {"age": 25, "localization": loc, "sex": "female"}
            jobs.append(job)

        # Create and fit encoder with known mapping
        encoder = LabelEncoder()
        encoder.fit(localizations)  # Fit with all possible localizations

        # Create a passthrough scaler
        scaler = StandardScaler()
        # Fit with dummy data matching the feature count (age, localization, sex)
        scaler.fit([[0, 0, 0], [1, 1, 1]])
        scaler.mean_ = np.array([0, 0, 0])  # Set mean to 0
        scaler.scale_ = np.array([1, 1, 1])  # Set scale to 1

        # Get features
        features, feature_names = extract_tabular_features(jobs, scaler, encoder)

        # Extract just the localization column (index 1)
        encoded_localizations = features[:, 1]

        # Get expected encodings for the first two localizations
        expected_encodings = encoder.transform(localizations[:2])

        # Ensure the arrays are the same type before comparison
        encoded_localizations = encoded_localizations.astype(np.int64)
        expected_encodings = expected_encodings.astype(np.int64)

        # Compare arrays
        np.testing.assert_array_equal(encoded_localizations, expected_encodings)

    def test_ordering_is_preserved(self):
        """Test that the ordering of features is preserved when processing the jobs."""
        # Create mock data with known values
        mock_jobs = [
            MagicMock(
                parameters={
                    "age": 25,
                    "localization": "ear",
                    "sex": "male",
                    "image": np.zeros((100, 100, 3)),
                }
            ),
            MagicMock(
                parameters={
                    "age": 40,
                    "localization": "face",
                    "sex": "female",
                    "image": np.ones((100, 100, 3)),
                }
            ),
        ]

        # Create and fit encoder with all possible localizations
        encoder = LabelEncoder()
        all_localizations = [loc[0] for loc in Requests.LOCALIZATION_CHOICES]
        encoder.fit(all_localizations)

        # Create a scaler with known transformation
        scaler = StandardScaler()
        # Fit with dummy data matching our feature dimensions
        sample_data = np.array([[25, 0, 1], [40, 1, 0]])  # age, loc, sex
        scaler.fit(sample_data)

        # Get features
        features, feature_names = extract_tabular_features(mock_jobs, scaler, encoder)

        # Get expected encoded value for 'ear'
        expected_ear_encoding = encoder.transform(["ear"])[0]

        # Transform through scaler to get expected scaled value
        expected_scaled_encoding = scaler.transform([[25, expected_ear_encoding, 1]])[
            0, 1
        ]

        # Compare the scaled, encoded value
        self.assertEqual(features[0, 1], expected_scaled_encoding)

        # Additional checks for other features if needed
        self.assertEqual(len(feature_names), 3)  # Verify we have all features
        self.assertIn("localization", feature_names)  # Verify localization is included

    def tearDown(self):
        """Teardown method for cleaning up after tests."""
        pass
