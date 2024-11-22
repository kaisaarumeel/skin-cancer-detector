import os
import time
from django.http import JsonResponse
from django.views import View

from ..models import Requests


class UploadPhoto(View):
    def post(self, request):

        # Checks if 'image' is in request.FILES
        if "image" not in request.FILES:
            return JsonResponse({"err": "No image provided"}, status=400)

        image = request.FILES["image"]
        file_extension = os.path.splitext(image.name)[1].lower()

        # Validating file extensions (accepts JPEG, PNG, JPG only)
        if file_extension not in [".jpeg", ".jpg", ".png"]:
            return JsonResponse(
                {"err": "Invalid file type. Only JPEG, JPG, and PNG are allowed."},
                status=400,
            )

        # Checks if localization or lesion type are present
        localization = request.data.get("localization")
        lesion_type = request.data.get("lesion_type")

        if not localization or not lesion_type:
            return JsonResponse(
                {"err": "Missing localization or lesion_type"}, status=400
            )

        try:
            # Saves the image data as binary to the Requests model
            image_data = image.read()

            # Creates the Request entry in the database
            request_entry = Requests.objects.create(
                user=request.user,  # Associates the image with the logged-in user
                image=image_data,  # Stores the image as binary data
                localization=localization,
                lesion_type=lesion_type,
                created_at=int(time.time()),  # Set the current timestamp
            )
            # Prepare the response data to return
            response_data = {
                "msg": "Image uploaded successfully!",
                "request_id": request_entry.request_id,
                "localization": request_entry.localization,
                "lesion_type": request_entry.lesion_type,
                "created_at": request_entry.created_at,
                "user": request_entry.user.username,
            }

            return JsonResponse(response_data, status=201)

        except Exception as e:
            return JsonResponse(
                {"err": f"Error processing image: {str(e)}"}, status=500
            )
