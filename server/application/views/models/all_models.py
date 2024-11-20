import base64
from django.http import JsonResponse
from django.views import View

from ...decorators import admin_only
from ...models import Model

class GetAllModels(View):
    @admin_only
    def get(self, request):

        # retrieve all models in the database
        models = Model.objects.all()

        models_data = [{
            "model_id": model.model_id,
            "created_at": model.created_at,
            "version": model.version,
            "weights": base64.b64encode(model.weights).decode('utf-8'),  # convert to base64 string, which is JSON-serializable
            "status": model.status,
        } for model in models]
        
        return JsonResponse({"models": models_data}, status=200)
        