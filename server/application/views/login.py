# views/login.py
from django.http import JsonResponse
from .base.base_login import BaseLogin
from ..decorators import load_json

class Login(BaseLogin):
    @load_json
    def post(self, request, check_admin=False):
        # Ensure that the request body has the required fields
        if not all([request.data["username"], request.data["password"]]):
            return JsonResponse({"err": "Missing fields"}, status=400)
        # Login via base class
        return self.base_login(request, request.data["username"], request.data["password"])