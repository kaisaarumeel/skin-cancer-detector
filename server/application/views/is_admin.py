from django.http import JsonResponse
from django.views import View

class IsAdmin(View):
    def get(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user has admin privileges (is staff or superuser)
            if request.user.is_admin:
                return JsonResponse({"is_admin": True, "username": request.user.username})
            else:
                return JsonResponse({"is_admin": False}) 
        else:
            return JsonResponse({"is_logged_in": False}, status=401)  # Unauthorized if not logged in
