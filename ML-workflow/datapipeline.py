import pandas as pd
import numpy as np
import sqlite3
from PIL import Image
from io import BytesIO
from sklearn.preprocessing import LabelEncoder

db_path = "db_images.sqlite3"
table_name = "images"

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


# function for preprocessing images
def preprocess_images(binary_data):
    # Load the image from binary data
    image = Image.open(BytesIO(binary_data)).convert("RGB")

    # Resize the image to 224x224
    image = image.resize((224, 224), Image.Resampling.LANCZOS)

    # Normalize to [0, 1]
    image_array = np.array(image) / 255.0

    return image_array


def feature_preprocessing(df):
    # Discarding the lesion_type feature
    df.drop(columns="lesion_type", axis=1, inplace=True)

    # dropping image_id column
    df.drop(columns=["image_id"], inplace=True)

    # Image preprocessing
    df["image"] = df["image"].apply(preprocess_images)

    # Label encoding the localization feature
    encoder = LabelEncoder()
    df["localization"] = encoder.fit_transform(df["localization"])
    # One-hot encoding sex feature
    df_encoded = pd.get_dummies(df, columns=["sex"], dtype=int, drop_first=True)

    return df_encoded


#### Data preprocess pipeline (Includin all steps) ####
def pre_process_data(db_path, table_name, row_limit=None, start_row=0):
    data = load_data(db_path, table_name, row_limit, start_row)
    cleaned_data = clean_data(data)
    pre_processessed_data = feature_preprocessing(cleaned_data)
    return pre_processessed_data

# Example 
preprocessed_data = pre_process_data(db_path, table_name)
print(preprocessed_data)
