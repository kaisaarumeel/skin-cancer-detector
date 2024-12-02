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
            return JsonResponse({"err": "Username already exists"}, status=400)
        
        # Validate age
        try:
            age = int(request.data["age"])
            if not (0 <= age <= 120):
                return JsonResponse({"err": "Age must be between 0 and 120"}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"err": "Age must be an integer"}, status=400)

        # Validate sex
        if request.data["sex"] not in ["female", "male"]:
            return JsonResponse({"err": "Sex must be either 'female' or 'male'"}, status=400)

        # Create the user
        user = Users.objects.using("default").create(
            username=request.data["username"],
            age=request.data["age"],
            sex=request.data["sex"],
            password=make_password(request.data["password"]),
            is_active=True,  # This user can now login
        )

        return JsonResponse({"msg": "User created"}, status=201)
