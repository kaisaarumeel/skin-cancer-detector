import cv2
import numpy as np
import os


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
