# Contributors:
# * Contributor: <rokanas@student.chalmers.se>
from django.http import JsonResponse
from django.views import View

from ...decorators import admin_only
from ...models import Model


class GetAllModels(View):
    @admin_only
    def get(self, request):

        # retrieve all models in the database
        models = Model.objects.all()

        models_data = [
            {
                "version": model.version,
                "created_at": model.created_at,
                "hyperparameters": model.hyperparameters,
            }
            for model in models
        ]

        return JsonResponse({"models": models_data}, status=200)
