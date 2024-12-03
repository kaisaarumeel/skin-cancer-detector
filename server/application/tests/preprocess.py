from django.test import TestCase
import numpy as np
import cv2
import os
from unittest.mock import MagicMock
from sklearn.preprocessing import StandardScaler, LabelEncoder
from ..models import Requests
from ..predictions.preprocess_user_data import (
    preprocess_images,
    extract_images,
    extract_tabular_features,
)


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
            result = preprocess_images(
                [self.valid_image, self.valid_image2], self.target_input_shape
            )

            # Assertions
            self.assertEqual(
                result.shape,
                (2, *self.target_input_shape, 3),
                f"Unexpected shape: {result.shape}",
            )
            self.assertTrue(
                result.dtype == np.float16, f"Unexpected dtype: {result.dtype}"
            )
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

        # Extract images
        result = extract_images(jobs)

        # Ensure that the result is an empty list
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

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
        self.assertTrue(
            all(isinstance(image, np.ndarray) for image in result)
        )  # Ensure each entry is an image array

    def test_extract_tabular_features_standardized(self):
        """Test the scaling of standardized features."""

        ############################ SETUP ############################

        # Mock data
        jobs = [
            MagicMock(parameters={"age": 30, "localization": "ear", "sex": "male"}),
            MagicMock(parameters={"age": 50, "localization": "face", "sex": "female"}),
        ]
        # Encoded representation of job data used to fit scaler
        # age, location (ear = 0, face = 1), sex (male = 1, female = 0)
        mock_training_data = [[30, 0, 1], [50, 1, 0]]

        # Create and fit mock scaler
        mock_scaler = StandardScaler()
        mock_scaler.fit(mock_training_data)

        # Mock the encoder
        mock_encoder = MagicMock()
        # This returns the encoded labels 0 and 1 when we pass it to the function under test
        mock_encoder.transform = MagicMock(side_effect=lambda x: [0, 1])

        ############################ TEST ############################

        # Call the function we are testing
        result = extract_tabular_features(jobs, mock_scaler, mock_encoder)

        # Assert the correctness of the results
        expected = mock_scaler.transform(mock_training_data)
        # Use numpy testing methods rather than python unittest,
        # in order to compare nested arrays
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_extract_tabular_features_encoding(self):
        """Test the encoding of localization labels."""

        ############################ SETUP ############################

        # Get the localization options from the model schema
        localizations = [loc[0] for loc in Requests.LOCALIZATION_CHOICES]
        # Create mock jobs
        jobs = [
            MagicMock(parameters={"age": 25, "localization": loc, "sex": "female"})
            for loc in localizations
        ]

        # Create and fit the mock encoder
        mock_encoder = LabelEncoder()
        mock_encoder.fit(localizations)

        # Mock scaler (not tested here, simply passes data through)
        mock_scaler = MagicMock()
        mock_scaler.transform = MagicMock(side_effect=lambda x: x)

        ############################ TEST ############################

        # Call the function we are testing
        result = extract_tabular_features(jobs, mock_scaler, mock_encoder)

        # Extract the encoded localizations
        encoded_localizations = [row[1] for row in result]

        # Assert the correctness of the encoding
        expected_encodings = mock_encoder.transform(localizations)

        # Use numpy testing methods to compare arrays
        np.testing.assert_array_equal(encoded_localizations, expected_encodings)

    def test_ordering_is_preserved(self):
        """Test that the ordering of features is preserved when processing the jobs."""

        ############################ SETUP ############################

        # Mock input data
        mock_jobs_batch = [
            MagicMock(
                parameters={
                    "age": 25,
                    "localization": "ear",
                    "sex": "male",
                    "image": np.random.rand(100, 100, 3),
                }
            ),
            MagicMock(
                parameters={
                    "age": 40,
                    "localization": "face",
                    "sex": "female",
                    "image": np.random.rand(100, 100, 3),
                }
            ),
            MagicMock(
                parameters={
                    "age": 60,
                    "localization": "neck",
                    "sex": "male",
                    "image": np.random.rand(100, 100, 3),
                }
            ),
        ]

        # Mock labels (same labels as in the mock jobs)
        mock_localization_labels = ["ear", "face", "neck"]

        # Expected model input shape and target image height and width
        model_input_shape = (64, 64, 3)
        target_image_size = (64, 64)

        # Mock scaler (not tested here, simply passes data through)
        mock_scaler = MagicMock()
        mock_scaler.transform = MagicMock(side_effect=lambda x: x)

        # Mock a fitted localization encoder
        mock_encoder = LabelEncoder()
        mock_encoder.fit(mock_localization_labels)

        ############################ TEST ############################

        # Extract and preprocess the images
        processed_images = preprocess_images(
            extract_images(mock_jobs_batch), target_image_size
        )

        # Extract tabular features
        tabular_features = extract_tabular_features(
            mock_jobs_batch, mock_scaler, mock_encoder
        )

        # Assertions to check that the ordering is kept intact
        for i, job in enumerate(mock_jobs_batch):

            # Assert that the image is correct
            expected_image = preprocess_images(
                [job.parameters["image"]], target_image_size
            )
            np.testing.assert_array_equal(expected_image[0], processed_images[i])

            # Assert that the age is correct
            expected_age = job.parameters["age"]
            self.assertEqual(expected_age, tabular_features[i, 0])

            # Assert that the localization is correct
            expected_localization = mock_encoder.transform(
                [job.parameters["localization"]]
            )
            self.assertEqual(expected_localization, tabular_features[i, 1])

            # Assert that the sex is correct ("male" = 1, "female" = 0)
            expected_sex = job.parameters["sex"].lower() == "male"
            self.assertEqual(expected_sex, tabular_features[i, 2])

    def tearDown(self):
        """Teardown method for cleaning up after tests."""
        pass
