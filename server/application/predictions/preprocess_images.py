import cv2
import numpy as np
import os

def preprocess_images(image_list, model):
    """
    Preprocesses a batch of images for model prediction.
    
    Args:
        image_list (list): List of image file paths or raw image arrays.
        model: The model to retrieve input shape from.
    
    Returns:
        np.ndarray: A batch of preprocessed images ready for model prediction.
    """

    preprocessed_images = []

    # Extract the input shape from the model
    target_input_shape = model.input_shape[0]

    target_height, target_width = target_input_shape[1:3]

    for image_data in image_list:
        # Load image from file if given as a path
        if isinstance(image_data, str):
            if not os.path.exists(image_data):
                raise FileNotFoundError(f"Image file not found: {image_data}")
            image = cv2.imread(image_data)
            if image is None:
                raise ValueError(f"Failed to load image from path: {image_data}")
        else:
            image = image_data  # Assume it's already a raw image array
        
        # Convert BGR to RGB 
        image = image[..., ::-1]

        # Resize the image to the model's input dimensions
        resized_image = cv2.resize(image, (target_width, target_height))

        # Normalize pixel values to [-1, 1] range 
        normalized_image = resized_image / 127.5 - 1.0

        # Ensure the image is in float16 format 
        normalized_image = normalized_image.astype(np.float16)

        preprocessed_images.append(normalized_image)

    # Convert to a numpy array and ensure the correct batch shape
    return np.array(preprocessed_images)
