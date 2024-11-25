from django.http import JsonResponse
from django.views import View

class IsLoggedIn(View):
    def get(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            return JsonResponse({"is_logged_in": True, "username": request.user.username})
        else:
            return JsonResponse({"is_logged_in": False}, status=401)
