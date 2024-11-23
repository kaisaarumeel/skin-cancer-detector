import numpy as np


def validate_input_data(processed_data, images, input_size):
    # Basic none checks
    assert processed_data is not None, "Processed data is None"
    assert images is not None, "Images data is None"
    # Images should be equal to the number of tabular features
    assert len(processed_data) == len(
        images
    ), "Mismatch between processed data and images length"
    # Ensure we got the correct image size
    assert (
        images.shape[1:] == input_size
    ), f"Image size mismatch. Expected {input_size}, got {images.shape[1:]}"
    # Ensure we have the correct columns in the processed data
    assert "age" in processed_data.columns, "Age column is missing from processed data"
    assert (
        "localization" in processed_data.columns
    ), "Localization column is missing from processed data"
    assert (
        "sex_male" in processed_data.columns
    ), "Sex column is missing from processed data"
    assert (
        "lesion_type" in processed_data.columns
    ), "Lesion type is column missing from processed data"
    # Ensure data types are correct
    assert processed_data["age"].dtype in [
        np.float64,
        np.int64,
    ], "Age column has incorrect dtype"
    assert processed_data["sex_male"].dtype in [
        np.int64,
        np.bool_,
    ], "Sex column has incorrect dtype"
    # Null checks
    assert not processed_data["age"].isnull().any(), "Age column contains null values"
    assert (
        not processed_data["lesion_type"].isnull().any()
    ), "Lesion type column contains null values"
    print("> MLTEST OK: Input data validation passed :)")


def validate_preprocessed_data(tabular_features_scaled, labels_cat, num_classes):
    # Check for nans
    assert not np.isnan(
        tabular_features_scaled
    ).any(), "Scaled features contain NaN values"
    assert not np.isinf(
        tabular_features_scaled
    ).any(), "Scaled features contain infinity values"
    # Ensure the number of columns in the one-hot encoded labels is equal to the number of classes
    assert (
        labels_cat.shape[1] == num_classes
    ), f"Incorrect number of classes in labels. Expected {num_classes}, got {labels_cat.shape[1]}"
    # Ensure one-hot encoded labels are properly formatted, we have zero tolerance for errors here
    # since these are basic arithmetic operations
    assert np.allclose(
        np.sum(labels_cat, axis=1), 1, rtol=0, atol=0
    ), "One-hot encoded labels are not properly formatted"
    print("> MLTEST OK: Preprocessed data validation passed :)")


def validate_split_data(X_img_train, X_img_val, X_tab_train, X_tab_val, y_train, y_val):
    # Ensure the lengths of the training and validation sets are equal
    assert (
        len(X_img_train) == len(X_tab_train) == len(y_train)
    ), "Training set size mismatch"
    assert (
        len(X_img_val) == len(X_tab_val) == len(y_val)
    ), "Validation set size mismatch"
    # Check for NaN values
    assert not np.isnan(
        X_tab_train
    ).any(), "Training tabular features contain NaN values"
    assert not np.isnan(
        X_tab_val
    ).any(), "Validation tabular features contain NaN values"
    assert not np.isnan(X_img_train).any(), "Training images contain NaN values"
    assert not np.isnan(X_img_val).any(), "Validation images contain NaN values"
    print("> MLTEST OK: Split data validation passed :)")


def validate_model_output(model, input_size, num_classes):
    # Generate random test data, which is fine since we're only interested in the model architecture
    test_img = np.random.random((1,) + input_size)
    test_tab = np.random.random((1, 3))  # 3 tabular features
    test_output = model.predict([test_img, test_tab])
    # Ensure the output shape is correct
    assert test_output.shape == (
        1,
        num_classes,
    ), f"Model output shape mismatch. Expected (1, {num_classes}), got {test_output.shape}"
    # Use allclose to ensure that the values are within a range of 1e-5
    assert np.allclose(
        np.sum(test_output, axis=1), 1, rtol=1e-5
    ), "Model output probabilities don't sum to 1"
    print("> MLTEST OK: Model architecture validation passed :)")
