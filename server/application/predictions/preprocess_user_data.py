import cv2
import numpy as np


def extract_images(jobs):
    """
    Extracts images from a list of jobs.

    Args:
        jobs (list): List of job objects. Each job object contains parameters, including an image.

    Returns:
        np.ndarray: A 2D numpy array where each column corresponds to an image extracted from the jobs.
    """

    # Extract images using list comprehension
    images = [job.parameters.get("image") for job in jobs]

    # Stack images in 2D array
    images = np.column_stack((images))

    return images


def preprocess_images(image_list, target_input_shape):
    """
    Preprocesses a batch of images for model prediction.

    Args:
        image_list (list): List of numpy image arrays.
        target_input_shape: The target dimensions of the images.

    Returns:
        np.ndarray: A batch of preprocessed images ready for model prediction.\n
        Resized to target dimensions and normalized to [-1, 1] range.
    """

    preprocessed_images = []

    # Process all images
    for image in image_list:
        # Resize the image to the model's input dimensions
        resized_image = cv2.resize(
            image, target_input_shape, interpolation=cv2.INTER_AREA
        )

        # Normalize pixel values to [-1, 1] range
        normalized_image = resized_image / 127.5 - 1.0

        # Ensure the image is in float16 format
        normalized_image = normalized_image.astype(np.float16)

        preprocessed_images.append(normalized_image)

    # Convert to a numpy array and return the images
    return np.array(preprocessed_images)


def extract_tabular_features(jobs, scaler, localization_encoder):
    """
    Extracts and preprocesses tabular features from a list of jobs for model prediction.

    Args:
        jobs (list): List of job objects. Each job contains parameters like age, localization, and sex.
        scaler (object): A fitted scaler (e.g., StandardScaler) used to standardize numerical features.
        localization_encoder (object): A fitted encoder (e.g., LabelEncoder) used to encode localization labels.

    Returns:
        np.ndarray: A 2D numpy array of standardized tabular features ready for model prediction.
    """

    # Extract features using list comprehension
    ages = [job.parameters.get("age") for job in jobs]
    localizations = [job.parameters.get("localization") for job in jobs]
    sexes = [job.parameters.get("sex").lower() == "male" for job in jobs]

    # Encode the localization labels
    localizations = localization_encoder.transform(localizations)

    # TODO one-hot encode localization

    # Stack features in 2D array
    tabular_features = np.column_stack((ages, localizations, sexes))

    # Standardize the distribution using the scaler
    tabular_features = scaler.transform(tabular_features)

    return tabular_features
