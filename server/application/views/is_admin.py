# Contributors:
# * Contributor: <kaisa.arumeel@gmail.com>
from django.http import JsonResponse
from django.views import View


class IsAdmin(View):
    def get(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user is an admin
            return JsonResponse({"is_admin": request.user.is_admin})
        else:
            return JsonResponse(
                {"is_logged_in": False}, status=401
            )  # Unauthorized if not logged in
