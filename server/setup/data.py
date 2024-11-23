import os
from pathlib import Path
import time
import django
import pandas as pd


# Progress callback for git clone
def progress_callback(op_code, cur_count, max_count, message):
    percentage = round(cur_count / max_count * 100)
    print(f"Progress: {percentage}%")


def assert_or_get_training_data():
    # Load relevant model
    from application.models import Data

    # Get the current training data size
    current_training_count = Data.objects.using("db_images").count()

    print("Current training data size is", current_training_count)
    # get user input
    user_input = input("Do you want to download the dataset? [y/n]: ")
    if user_input.lower() != "y":
        print("Data validated")
        return

    # Prompt the user if they want to delete the current data
    user_input = input("Do you want to delete the current data? [y/n]: ")
    if user_input.lower() == "y":
        print("Deleting current data, this might take some time...")
        Data.objects.using("db_images").all().delete()

    temp_dir = Path("temp")

    # Allow user to override the dataset url
    DATASET_URL = os.environ.get("DATASET_URL")

    if not DATASET_URL:
        print("DATASET_URL not set, using default")
        DATASET_URL = "https://github.com/rokanas/dit826-data.git"
    if not temp_dir.exists():
        import git

        print("Downloading training data")
        temp_dir.mkdir()
        git.Repo.clone_from(DATASET_URL, temp_dir, progress=progress_callback)

    df = pd.read_csv(temp_dir / "HAM10000_metadata.csv")

    # Take the image_id column value and find the corresponding image in the HAM10000_images folder
    # then save that filename in the image_path column
    df["image_path"] = df["image_id"].apply(
        lambda x: temp_dir / "HAM10000_images" / f"{x}.jpg"
    )

    # Save all images and the metadata in the database
    for index, row in df.iterrows():
        # Load the image binary
        with open(row["image_path"], "rb") as f:
            # Read the image binary
            image_binary = f.read()
            try:
                # Check if the image already exists
                Data.objects.using("db_images").get(image_id=row["image_id"])
            except Data.DoesNotExist:
                try:
                    # If any of these rows are missing, set them to None
                    age = row["age"]
                    if pd.isna(age):
                        age = None

                    sex = row["sex"]
                    if pd.isna(sex):
                        sex = None

                    localization = row["localization"]
                    if pd.isna(localization):
                        localization = None

                    # Insert the datapoint
                    Data.objects.using("db_images").create(
                        image_id=row["image_id"],
                        image=image_binary,
                        age=age,
                        sex=sex,
                        localization=localization,
                        lesion_type=row["dx"],
                        created_at=int(time.time()),
                    )
                except Exception as e:
                    print("Unexpected error: ", e)
                    break
            print(f"Loading training data: {round(index / len(df) * 100)}%")
    print("Training data size is", Data.objects.using("db_images").count())
    # Remove the temp directory
    import shutil

    shutil.rmtree(temp_dir)
