# views/login.py
from django.http import JsonResponse

from ..decorators import load_json
from .base.base_login import BaseLogin


class Login(BaseLogin):
    @load_json
    def post(self, request, check_admin=False):
        # First check if all required fields exist in request.data
        required_fields = ['username', 'password']
        if not all(field in request.data for field in required_fields):
            return JsonResponse({"err": "Missing fields"}, status=400)
        
        # Then check if any of the fields are empty or None
        if not all(request.data[field] for field in required_fields):
            return JsonResponse({"err": "Fields cannot be empty"}, status=400)
        
        # Login via base class
        return self.base_login(
            request, request.data["username"], request.data["password"]
        )
