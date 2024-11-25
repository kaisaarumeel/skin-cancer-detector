import os
import time
import json
import base64
from django.http import JsonResponse
from django.views import View
from django.core.files.base import ContentFile
from ..models import Requests
from ..decorators import login_required
from .jobs.prediction import add_prediction_job, PREDICTIONS


class UploadPhoto(View):
    @login_required
    def post(self, request):
        # Parse JSON data from the request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"err": "Invalid JSON format"}, status=400)

        # Extract and validate Base64 image data
        image_base64 = data.get("image")
        if not image_base64:
            return JsonResponse({"err": "No image file provided"}, status=400)

        try:
            # Decode Base64 image
            format, imgstr = image_base64.split(";base64,")
            ext = format.split("/")[-1]  # Extract the file extension from the MIME type
            image_data = ContentFile(base64.b64decode(imgstr), name=f"uploaded_image.{ext}")
        except (ValueError, IndexError, base64.binascii.Error):
            return JsonResponse({"err": "Invalid Base64 image format"}, status=400)

        # Validate other required fields
        localization = data.get("localization")
        lesion_type = data.get("lesion_type")
        if not localization or not lesion_type:
            return JsonResponse(
                {"err": "Missing or empty required JSON fields"}, status=400
            )

        try:
            # Create a new entry in the Requests model
            request_entry = Requests.objects.create(
                user=request.user,
                image=image_data,
                localization=localization,
                lesion_type=lesion_type,
                created_at=int(time.time()),
            )

            # Call the prediction job
            parameters = {
                "request_id": request_entry.request_id,
                "user": request.user.username,
                "localization": request_entry.localization,
                "lesion_type": request_entry.lesion_type,
            }
            job = add_prediction_job(parameters)  # Create and process the job

            # Prepare the response data
            response_data = {
                "msg": "Image uploaded successfully!",
                "request_id": request_entry.request_id,
                "job_id": job.job_id,
                "localization": request_entry.localization,
                "lesion_type": request_entry.lesion_type,
                "created_at": request_entry.created_at,
                "user": request_entry.user.username,
            }

            return JsonResponse(response_data, status=201)

        except Exception as e:
            return JsonResponse({"err": f"Unexpected error: {str(e)}"}, status=500)
