# Contributors:
# * Contributor: <alexandersafstrom@proton.me>
# * Contributor: <elindstr@student.chalmers.se>
import os
import pickle
import gc
from .preprocess import clean_data, load_data, feature_preprocessing


def query_db_or_cache(
    clear_cache=False,
    test=False,
    db_name="db_images.sqlite3",
    images_table_name="images",
    row_limit=None,
    start_row=0,
    cache_dir="cache",
    test_data_dir="test_data",
    tabular_features="tabular_data.pkl",
    lesion_encoder="lesion_type_encoder.pkl",
    localization_encoder_fname="localization_encoder.pkl",
    images="images.pkl",
    requested_size=(224, 224),
):
    # We need to know where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create cache dir. We dont need to do this for test data as it will be present in repo for CI
    cache_dir = os.path.join(script_dir, cache_dir)
    os.makedirs(cache_dir, exist_ok=True)

    # Define cache paths
    PROCESSED_DATA_PATH = os.path.join(script_dir, cache_dir, tabular_features)
    LESION_ENCODER_PATH = os.path.join(script_dir, cache_dir, lesion_encoder)
    LOCALIZATION_ENCODER_PATH = os.path.join(
        script_dir, cache_dir, localization_encoder_fname
    )
    IMAGES_PATH = os.path.join(script_dir, cache_dir, images)

    # Define test data paths
    test_data_dir = os.path.join(script_dir, test_data_dir)
    TEST_PROCESSED_DATA_PATH = os.path.join(script_dir, test_data_dir, tabular_features)
    TEST_LESION_ENCODER_PATH = os.path.join(script_dir, test_data_dir, lesion_encoder)
    TEST_LOCALIZATION_ENCODER_PATH = os.path.join(
        script_dir, test_data_dir, localization_encoder_fname
    )
    TEST_IMAGES_PATH = os.path.join(script_dir, test_data_dir, images)

    # Update the db_name to be relative to the script location
    db_name = os.path.join(script_dir, db_name)

    # Try to load cached data (if it exists) and this is not a test run
    if (
        not clear_cache
        and not test
        and os.path.exists(PROCESSED_DATA_PATH)
        and os.path.exists(LESION_ENCODER_PATH)
        and os.path.exists(LOCALIZATION_ENCODER_PATH)
    ):
        print("Loading cached processed data...")
        with open(PROCESSED_DATA_PATH, "rb") as f:
            processed_data = pickle.load(f)
        with open(LESION_ENCODER_PATH, "rb") as f:
            lesion_type_encoder = pickle.load(f)
        with open(LOCALIZATION_ENCODER_PATH, "rb") as f:
            localization_encoder = pickle.load(f)
        with open(IMAGES_PATH, "rb") as f:
            images = pickle.load(f)
        print("Cached data loaded successfully")
        return processed_data, lesion_type_encoder, localization_encoder, images

    # Try to load cached test data (if it exists) and this is a test run
    if (
        not clear_cache
        and test
        and os.path.exists(TEST_PROCESSED_DATA_PATH)
        and os.path.exists(TEST_LESION_ENCODER_PATH)
        and os.path.exists(TEST_LOCALIZATION_ENCODER_PATH)
    ):
        print("Loading cached test data...")
        with open(TEST_PROCESSED_DATA_PATH, "rb") as f:
            processed_data = pickle.load(f)
        with open(TEST_LESION_ENCODER_PATH, "rb") as f:
            lesion_type_encoder = pickle.load(f)
        with open(TEST_LOCALIZATION_ENCODER_PATH, "rb") as f:
            localization_encoder = pickle.load(f)
        with open(TEST_IMAGES_PATH, "rb") as f:
            images = pickle.load(f)
        print("Cached test data loaded successfully")
        return processed_data, lesion_type_encoder, localization_encoder, images

    # If the data is not cached, we must load and process it

    # Load and process data
    print("Loading data...")
    image_data_df = load_data(
        db_path=db_name,
        table_name=images_table_name,
        row_limit=row_limit,
        start_row=start_row,
    )
    print("Cleaning data...")

    # Clean the data from duplicates and missing values
    cleaned_data = clean_data(image_data_df)

    # Drop the image_data_df DataFrame to free up memory
    del image_data_df
    gc.collect()

    print("Processing features...")
    # Process the data
    processed_data, lesion_type_encoder, localization_encoder, images = (
        feature_preprocessing(cleaned_data, requested_size)
    )

    # Drop the cleaned_data DataFrame to free up memory
    del cleaned_data
    gc.collect()

    # Cache the processed data
    print("Saving processed data to cache...")
    if test:
        with open(TEST_PROCESSED_DATA_PATH, "wb") as f:
            pickle.dump(processed_data, f)
        with open(TEST_LESION_ENCODER_PATH, "wb") as f:
            pickle.dump(lesion_type_encoder, f)
        with open(TEST_LOCALIZATION_ENCODER_PATH, "wb") as f:
            pickle.dump(localization_encoder, f)
        with open(TEST_IMAGES_PATH, "wb") as f:
            pickle.dump(images, f)
        print("Test data cached successfully")
        return processed_data, lesion_type_encoder, localization_encoder, images

    # Cache the processed data (non-test)
    with open(PROCESSED_DATA_PATH, "wb") as f:
        pickle.dump(processed_data, f)
    with open(LESION_ENCODER_PATH, "wb") as f:
        pickle.dump(lesion_type_encoder, f)
    with open(LOCALIZATION_ENCODER_PATH, "wb") as f:
        pickle.dump(localization_encoder, f)
    with open(IMAGES_PATH, "wb") as f:
        pickle.dump(images, f)
    print("Data cached successfully")
    return processed_data, lesion_type_encoder, localization_encoder, images
