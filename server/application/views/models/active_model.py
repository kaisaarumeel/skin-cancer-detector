from django.http import JsonResponse
from django.views import View

from ...models import Model

class getActiveModel(View):
    def get(self, request, check_admin=True):
        try:
            active_model = Model.objects.get(status="active")
            return JsonResponse({
                "model_id": active_model.model_id,
                "created_at": active_model.created_at,
                "version": active_model.version,
                "weights": active_model.weights,
                # "status": active_model.status
            })
        
        except Model.DoesNotExist:
            return JsonResponse({"err": "No active model found"}, status=404)
        
    def put(self, request):
        try: 
            new_model = Model.objects.get(request.model_id)