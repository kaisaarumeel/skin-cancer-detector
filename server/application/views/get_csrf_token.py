# Contributors:
# * Contributor: <rokanas@student.chalmers.se>
# * Contributor: <elindstr@student.chalmers.se>
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie


# decorator method ensures token is written to browser cookies
@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFToken(View):
    def get(self, request):
        return JsonResponse({"message": "CSRF cookie set"}, status=200)
