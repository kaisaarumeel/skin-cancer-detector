from django.http import JsonResponse
from django.views import View

from ...models import Model

class GetAllModels(View):
    def get(self, request, check_admin=True):

        models = Model.objects.all()

        # Check if any models exist in database
        if not models.exists():  
            return JsonResponse({"err": "No models found"}, status=404)

        models_data = [{
            "model_id": model.model_id,
            "created_at": model.created_at,
            "version": model.version,
            "weights": model.weights,
            "status": model.status,
        } for model in models]
        
        return JsonResponse({models_data}, status=200)
        