import os
import time
import zipfile
import shutil
import pandas as pd
from pathlib import Path
from django.http import JsonResponse
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import File
from ..decorators import admin_only
from ..models import Data


class AddData(View):
    @admin_only
    def post(self, request, *args, **kwargs):
        try:
            # check that request contains a file
            if "file" not in request.FILES:
                return JsonResponse({"err": "No file provided"}, status=400)

            # check that file is a zip file
            data_file = request.FILES["file"]
            if not zipfile.is_zipfile(data_file):
                return JsonResponse({"err": "File is not a zip file"}, status=400)

            # create temp folder for extracting zip contents using django storage backend
            temp_zip_path = default_storage.save(
                f"temp/{data_file.name}", File(data_file)
            )
            temp_dir = Path(temp_zip_path).parent

            try:
                # extract zip file
                with zipfile.ZipFile(temp_dir / data_file.name, "r") as zipdata:
                    zipdata.extractall(temp_dir)
            except Exception as e:
                return JsonResponse({"err": str(e)}, status=500)

            # check that CSV file exists
            metadata_path = temp_dir / "metadata.csv"
            if not metadata_path.exists():
                return JsonResponse(
                    {"err": "Metadata CSV not found in zip file"}, status=400
                )

            # load the metadata CSV
            df = pd.read_csv(metadata_path)

            # verify image folder
            images_path = temp_dir / "images"
            if not images_path.exists():
                return JsonResponse(
                    {"err": "Images folder not found in zip file"}, status=400
                )

            valid_extensions = [".jpeg", ".jpg", ".png"]

            # insert image paths in dictionary for faster lookups
            image_files = {}
            for file in os.listdir(images_path):
                # extract image extensions and validate
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension in valid_extensions:
                    image_id = os.path.splitext(file)[
                        0
                    ]  # get image name without the extension
                    image_files[image_id] = (
                        images_path / file
                    )  # image name is key, path is value

            # process and save each data entry to image db
            for index, row in df.iterrows():
                image_id = str(row["image_id"])
                image_path = image_files.get(image_id)  # get image path from dictionary

                if not image_path or not image_path.exists():
                    print(
                        f"Warning: image {row['image_id']} not found or invalid and will be skipped"
                    )
                    continue

                with open(image_path, "rb") as f:
                    image_binary = f.read()

                try:
                    # Check if the image already exists
                    Data.objects.using("db_images").get(image_id=row["image_id"])
                except Data.DoesNotExist:
                    try:
                        # If any of these rows are missing, set them to None
                        age = row["age"] if pd.notna(row["age"]) else None
                        sex = row["sex"] if pd.notna(row["sex"]) else None
                        localization = (
                            row["localization"]
                            if pd.notna(row["localization"])
                            else None
                        )

                        # Save the new data entry
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

            # clean up temporary files
            shutil.rmtree(temp_dir)

            # return success response
            training_data_size = Data.objects.using("db_images").count()
            return JsonResponse(
                {
                    "message": "Training data uploaded successfully",
                    "training_data_size": training_data_size,
                }
            )

        except Exception as e:
            return JsonResponse({"err": str(e)}, status=500)
