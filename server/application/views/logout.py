from django.contrib.auth import logout
from django.http import JsonResponse
from django.views import View

class Logout(View):
    def post(self, request):
        # Log out the user
        logout(request)
        return JsonResponse({"msg": "Successfully logged out"}, status=200)
