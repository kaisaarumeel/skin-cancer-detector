from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views import View

from ..decorators import load_json, login_required
from ..models import Users


class ChangePassword(View):
    @load_json
    @login_required  # Ensures that only logged in users can access this view
    def post(self, request):
        # First check if all required fields exist in request.data
        required_fields = ["new_password"]
        if not all(field in request.data for field in required_fields):
            return JsonResponse({"err": "Missing fields"}, status=400)

        # Then check if any of the fields are empty or None
        if not all(request.data[field] for field in required_fields):
            return JsonResponse({"err": "Fields cannot be empty"}, status=400)

        # Change the password
        request.user.password = make_password(request.data["new_password"])
        request.user.save()

        # Update the session hash
        update_session_auth_hash(request, request.user)
        return JsonResponse({"msg": "Password changed"}, status=200)
