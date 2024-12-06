from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
class GetCSRFToken(View):
    def get(self, request):
        return JsonResponse({'message': 'CSRF cookie set'})