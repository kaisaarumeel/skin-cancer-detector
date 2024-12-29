# Contributors:
# * Contributor: <kaisa.arumeel@gmail.com>
# * Contributor: <rokanas@student.chalmers.se>
# * Contributor: <elindstr@student.chalmers.se>
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views import View


class Logout(View):
    def post(self, request):
        # Log out the user
        logout(request)
        response = JsonResponse({"msg": "Successfully logged out"}, status=200)
        response.delete_cookie("csrftoken")
        return response
