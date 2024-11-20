import json
from functools import wraps

from django.http import JsonResponse


# Decorator to ensure that the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return f(self, request, *args, **kwargs)
        else:
            return JsonResponse({"err": "Unauthorized"}, status=401)

    return decorated_function


# Decorator to preload the request body as JSON
def load_json(f):
    @wraps(f)
    def decorated_function(self, request, *args, **kwargs):
        try:
            request.data = json.loads(request.body)
        except Exception as e:
            print(e)
            return JsonResponse({"err": "Invalid JSON"}, status=400)
        return f(self, request, *args, **kwargs)

    return decorated_function


# Decorator to ensure that the user is an admin
def admin_only(f):
    @wraps(f)
    def decorated_function(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return f(self, request, *args, **kwargs)
        else:
            return JsonResponse({"err": "Unauthorized"}, status=401)

    return decorated_function