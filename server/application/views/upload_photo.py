import os
import time
import json
from django.http import JsonResponse
from django.views import View
from django.core.files.storage import default_storage
from ..models import Requests
from ..decorators import login_required


class UploadPhoto(View):
    @login_required
    def post(self, request):

        # Check for the image file
        uploaded_image = request.FILES.get("image")
        if not uploaded_image:
            return JsonResponse({"err": "No image file provided"}, status=400)

        # Check for JSON data
        json_data = request.POST.get("data")
        if not json_data:
            return JsonResponse({"err": "No JSON data provided"}, status=400)

        # Parse JSON data
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            return JsonResponse({"err": "Invalid JSON format"}, status=400)

        # Validate JSON fields
        localization = json_data.get("localization")
        lesion_type = json_data.get("lesion_type")
        if not localization or not lesion_type:
            return JsonResponse(
                {"err": "Missing or empty required JSON fields"}, status=400
            )

        try:
            # Save the image temporarily
            temp_image_path = default_storage.save(
                f"temp/{time.time()}_{uploaded_image.name}", uploaded_image
            )

            # Read the image data
            with open(temp_image_path, "rb") as img_file:
                image_data = img_file.read()

            # Create a new entry in the Requests model
            request_entry = Requests.objects.create(
                user=request.user,
                image=image_data,
                localization=localization,
                lesion_type=lesion_type,
                created_at=int(time.time()),
            )

            # Prepare the response data
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
            return JsonResponse({"err": f"Unexpected error: {str(e)}"}, status=500)

        finally:
            # Clean up the temporary image file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
