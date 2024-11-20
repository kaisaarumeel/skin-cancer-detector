from django.http import JsonResponse
from django.views import View

from ...decorators import admin_only
from ...models import Model

class GetActiveModel(View):
    @admin_only
    def get(self, request):
        try:
            # find and return currently active model in the database
            active_model = Model.objects.get(status="active")
            return JsonResponse({
                "model_id": active_model.model_id,
                "created_at": active_model.created_at,
                "version": active_model.version,
                "weights": active_model.weights,
                # "status": active_model.status #technically redundant
            })
        
        except Model.DoesNotExist:
            return JsonResponse({"err": "No active model found"}, status=404)
