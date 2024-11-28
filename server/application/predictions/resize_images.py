import cv2
import numpy as np

def preprocess_images(image_list, model_input_size):
    """
    Preprocesses a batch of images for model prediction.
    
    Args:
        image_list (list): List of image file paths or raw image arrays.
        model_input_size (tuple): The (height, width, channels) of the model's input size.
    
    Returns:
        np.ndarray: A batch of preprocessed images ready for model prediction.
    """
    preprocessed_images = []
    
    target_height, target_width = model_input_size[:2]
    print("model height", target_height)
    print("model width", target_width)
   
    for image_data in image_list:
        # Load image from file if given as a path
        if isinstance(image_data, str):
            image = cv2.imread(image_data)
        else:
            image = image_data  # Assume it's already a raw image array
        
        print(f"Original image size: {image.shape[0]}x{image.shape[1]} (HxW)")

        # Resize the image to the model's input dimensions
        resized_image = cv2.resize(image, (target_width, target_height))
        
        # Normalize pixel values (optional, depends on model's training process)
        normalized_image = resized_image / 255.0
        
        preprocessed_images.append(normalized_image)
        print(f"After image size: {normalized_image.shape[0]}x{normalized_image.shape[1]} (HxW)")
    
    # Convert to a numpy array and ensure the correct batch shape
    return np.array(preprocessed_images)
