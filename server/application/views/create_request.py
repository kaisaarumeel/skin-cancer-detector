import time
import base64
import uuid
from django.http import JsonResponse
from django.views import View
from ..models import Users
from ..decorators import login_required, load_json
from .jobs.state import PREDICTION_JOBS
from .jobs.job import Job
from io import BytesIO
from PIL import Image


def fix_base64_padding(base64_str):
    """Fix missing padding in Base64 strings."""
    missing_padding = len(base64_str) % 4
    if missing_padding:
        base64_str += "=" * (4 - missing_padding)
    return base64_str


class CreateRequest(View):
    @login_required
    @load_json
    def post(self, request):
        global PREDICTION_JOBS
        data = request.data

        if not data:
            return JsonResponse({"err": "No JSON data provided"}, status=400)

        # Validate required JSON field
        localization = data.get("localization")
        image_base64 = data.get("image")
        # Handle case when JSON exists but has no data (empty JSON object)
        if not data:
            return JsonResponse({"err": "No JSON data provided"}, status=400)
        if not localization:
            return JsonResponse(
                {"err": "Missing or empty required field: 'localization'"}, status=400
            )
        if not image_base64:
            return JsonResponse({"err": "No image file provided"}, status=400)
        try:
            image_base64 = fix_base64_padding(image_base64)
            image_data = base64.b64decode(image_base64)

            # Create a BytesIO object from the decoded bytes
            image_stream = BytesIO(image_data)

            # Open the image using Pillow
            image = Image.open(image_stream)

            allowed_formats = ["JPEG", "PNG", "JPG"]

            if image.format not in allowed_formats:
                return JsonResponse({"err": "Unsupported image format"}, status=400)
        except Exception as e:
            return JsonResponse({"err": "Invalid Base64"}, status=400)

        user = Users.objects.get(username=request.user.username)
        parameters = {
            "username": user.username,
            "age": user.age,
            "sex": user.sex,
            "localization": localization,
            "image":image,
        }

        job = Job(
            job_id=str(uuid.uuid4()), start_time=int(time.time()), parameters=parameters
        )
        PREDICTION_JOBS.append(job)
        return JsonResponse(
            {
                "msg": "Image uploaded successfully!",
            },
            status=201,
        )
