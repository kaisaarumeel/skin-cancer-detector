# Contributors:
# * Contributor: <alexandersafstrom@proton.me>
# base/base_login.py
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views import View


# The base class used for logging in.
# It is not directly used but rather inherited by other classes.
class BaseLogin(View):
    def base_login(self, request, username, password):
        if not all([username, password]):
            return JsonResponse({"err": "Missing fields"}, status=400)

        # Authenticate via django's built-in authentication system
        user = authenticate(request, username=username, password=password)

        # If user is not None, then credentials are valid
        if user is not None:
            # Generate a session for the user
            login(request, user)
            return JsonResponse(
                {"msg": "Login successful", "username": user.username}, status=200
            )
        else:
            return JsonResponse({"err": "Invalid credentials"}, status=401)
