from django.http import JsonResponse
from django.views import View
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password

from ..models import Users
from ..decorators import login_required,load_json
class ChangePassword(View):
    @load_json
    @login_required # Ensures that only logged in users can access this view
    def post(self, request):
        # Ensure that the request body has the required fields
        if not all([request.data["new_password"]]): 
            return JsonResponse({"msg":"Missing fields"}, status=400)
            
        # Change the password
        request.user.password=make_password(request.data["new_password"])
        request.user.save()

        # Update the session hash
        update_session_auth_hash(request,request.user)
        return JsonResponse({"msg":"Password changed"}, status=200)

    
