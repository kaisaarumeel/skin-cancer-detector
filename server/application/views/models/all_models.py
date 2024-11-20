from django.http import JsonResponse
from django.views import View

from ...decorators import admin_only
from ...models import Model

class GetAllModels(View):
    @admin_only
    def get(self, request):

        # retrieve all models in the database
        models = Model.objects.all()

        # check if list of models is empty
        if not models.exists():  
            return JsonResponse({"err": "No models found"}, status=404)

        models_data = [{
            "model_id": model.model_id,
            "created_at": model.created_at,
            "version": model.version,
            "weights": model.weights,
            "status": model.status,
        } for model in models]
        
        return JsonResponse({"models": models_data}, status=200)
        