# Contributors:
# * Contributor: <alexandersafstrom@proton.me>
# * Contributor: <elindstr@student.chalmers.se>
import pandas as pd
import numpy as np
import sqlite3
from PIL import Image
from io import BytesIO
from sklearn.preprocessing import LabelEncoder
import cv2
import gc
from tqdm import tqdm


def load_data(db_path, table_name, row_limit=None, start_row=0):
    # DB connection
    connection = sqlite3.connect(db_path)

    # Load images
    query = f"SELECT * FROM {table_name}"
    if row_limit:
        query += f" LIMIT {row_limit}"
    if start_row:
        query += f" OFFSET {start_row}"
    query += ";"

    # Load Data into Pandas DataFrame
    df = pd.read_sql_query(query, connection)
    # Close the Connection
    connection.close()
    return df


def clean_data(df):
    # Drop data points with empty values such as Nan
    df.dropna(inplace=True)

    # check for the correct format of each property
    df["sex"] = df["sex"].str.lower()  # lower case for "sex" property
    valid_sex = ["female", "male"]
    df = df[df["sex"].isin(valid_sex)]

    # check for the localization values
    # unique_localizations = df['localization'].unique()
    df.loc[:, "localization"] = df["localization"].str.lower()
    valid_localization = [
        "scalp",
        "ear",
        "face",
        "back",
        "trunk",
        "chest",
        "upper extremity",
        "abdomen",
        "lower extremity",
        "genital",
        "neck",
        "hand",
        "foot",
        "acral",
    ]
    df = df[df["localization"].isin(valid_localization)]

    # drop duplicated images
    df.drop_duplicates(subset=["image", "image_id"], inplace=True, keep="last")

    # Clean age with wrong format and wrong range
    df["age"] = pd.to_numeric(
        df["age"], errors="coerce"
    )  # Makes sure Age is a numerical value
    df = df[(df["age"] > 0) & (df["age"] <= 120)]

    return df


def preprocess_images(binary_data, requested_size):
    # Convert binary to numpy array
    img = np.frombuffer(binary_data, np.uint8)

    # Use cv2 to decode the image
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    # Convert BGR to RGB using array indexing
    # We do this by targeting all rows and cols
    # and then reversing only the last axis, which are
    # the color channels
    img = img[..., ::-1]

    # Get current dimensions
    h, w = img.shape[:2]
    target_h, target_w = requested_size

    # If the dimensions are not the same, resize
    if (h, w) != requested_size:
        img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)

    # Normalize to [-1, 1] range, so that we dont
    # have to do it later and have compatibility with
    # pre-trained models
    img = img / 127.5 - 1.0

    # Ensure the image is in float16 format
    # to save memory
    img = img.astype(np.float16)

    return img


def feature_preprocessing(df, requested_size):
    """Feature preprocessing with memory optimizations"""
    # Drop columns in-place to save memory
    df.drop(columns=["image_id"], inplace=True)

    # Process images and store as 4D array directly
    # The reason why it is a 4D array is because it we have n images,
    # each image has a height, width and 3 channels (RGB)
    # which results in a 4D array of shape (n, height, width, 3)
    print("Processing images...")

    # Add a progress bar using tqdm for visual feedback
    tqdm.pandas(desc="Processing images")

    # Pre-allocate array with the correct shape and data type
    # We use float16 to save memory
    images = np.zeros(
        (len(df), requested_size[0], requested_size[1], 3), dtype=np.float16
    )  # Pre-allocate array

    # For each image, preprocess and store in the pre-allocated array
    # we use enumerate to get the index and image data
    # tqdm is wrapped around the loop and shows the progress
    # of the loop
    for i, img_data in enumerate(tqdm(df["image"])):
        images[i] = preprocess_images(img_data, requested_size)

    # Remove image column from df since we have it in separate array
    df = df.drop(columns=["image"])

    # Encode categorical features
    # we need to have two separate encoders for the two features
    # as they are different types of features
    localization_encoder = LabelEncoder()
    lesion_type_encoder = LabelEncoder()

    # Label encoding the localization feature
    localization_encoder = LabelEncoder()
    df["localization"] = localization_encoder.fit_transform(df["localization"])

    # Label encoding the lesion_type feature
    lesion_type_encoder = LabelEncoder()

    df["lesion_type"] = lesion_type_encoder.fit_transform(df["lesion_type"])

    # One-hot encoding sex feature
    df_encoded = pd.get_dummies(df, columns=["sex"], dtype=int, drop_first=True)

    # Free up memory
    gc.collect()

    # We need the lesion_type_encoder for training
    # We need to store the localization_encoder with the model to preprocess user data
    return df_encoded, lesion_type_encoder, localization_encoder, images
