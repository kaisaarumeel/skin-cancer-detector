from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views import View

from ..decorators import load_json
from ..models import Users


class Register(View):
    @load_json
    def post(self, request):
        # First check if all required fields exist in request.data
        required_fields = ["username", "password", "age", "sex"]
        if not all(field in request.data for field in required_fields):
            return JsonResponse({"err": "Missing fields"}, status=400)

        # Then check if any of the fields are empty or None
        if not all(request.data[field] for field in required_fields):
            return JsonResponse({"err": "Fields cannot be empty"}, status=400)

        # Check if the user already exists
        if (
            Users.objects.using("default")
            .filter(username=request.data["username"])
            .exists()
        ):
            return JsonResponse({"err": "User already exists"}, status=400)

        # Create the user
        user = Users.objects.using("default").create(
            username=request.data["username"],
            age=request.data["age"],
            sex=request.data["sex"],
            password=make_password(request.data["password"]),
            is_active=True,  # This user can now login
        )

        return JsonResponse({"msg": "User created"}, status=201)
