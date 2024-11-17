from django.http import JsonResponse
from django.views import View
from django.contrib.auth.hashers import make_password
from ..models import Users
from ..decorators import load_json

class Register(View):
    @load_json
    def post(self, request):
        # Ensure that the request body has the required fields
        if not all([request.data["username"], request.data["password"], request.data["age"], request.data["sex"]]):
            return JsonResponse({"msg":"Missing fields"}, status=400)

        # Check if the user already exists
        if Users.objects.using("default").filter(username=request.data["username"]).exists():
            return JsonResponse({"msg":"User already exists"}, status=400)

        # Create the user   
        user = Users.objects.using("default").create(
            username=request.data["username"],
            age=request.data["age"],
            sex=request.data["sex"],
            password=make_password(request.data["password"]),
            is_active=True # This user can now login
        )

        return JsonResponse({"msg":"User created"}, status=201)
    
