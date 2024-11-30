import time
import base64
import numpy as np
from django.http import JsonResponse
from django.views import View
from django.db import transaction, DatabaseError
from ..models import Users, Requests
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

        # Validate required JSON fields
        localization = data.get("localization")
        image_base64 = data.get("image")
        # Handle case when JSON exists but has no data (empty JSON object)
        if not data:
            return JsonResponse({"err": "No JSON data provided"}, status=400)
        if not localization:
            return JsonResponse(
                {"err": "Missing or empty required field: 'localization'"}, status=400
            )
        if localization not in dict(Requests.LOCALIZATION_CHOICES):
            return JsonResponse({"err": "Invalid localization value."}, status=400)
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

        # Convert image from pillow format to np.uint8,
        # for consistency with the rest of the program
        image_array = np.array(image, np.uint8)

        # Get the corresponding user from the database
        user = Users.objects.get(username=request.user.username)

        # Get current time of creating request
        created_at = int(time.time())

        # Insert new request into database
        try:
            # Treat insertion as atomic, i.e. rollback if there are any exceptions
            # Note that the foreign key is automatically resolved when passing the user object
            with transaction.atomic():
                new_request = Requests.objects.create(
                    created_at=created_at,
                    image=image_data,
                    localization=localization,
                    user=user,
                )

                # Retrieve the generated request id from the database insertion
                request_id = new_request.request_id

        except DatabaseError as e:
            message = (
                "An error occured when processing the request. Please try again later."
            )
            # Show full stacktrace only to admin users
            if user.is_admin:
                message = f"Database insertion error: {str(e)}"
            return JsonResponse({"err": message}, status=500)

        # Wrap all relevant request parameters in an object
        parameters = {
            "request_id": request_id,
            "age": user.age,
            "sex": user.sex,
            "localization": localization,
            "image": image_array,
        }

        # Create new Job and add it to the global queue
        job = Job(job_id=request_id, start_time=created_at, parameters=parameters)
        PREDICTION_JOBS.put(job)

        return JsonResponse(
            {
                "msg": "Request created successfully! Results pending.",
                "request_id": request_id,
            },
            status=201,
        )
