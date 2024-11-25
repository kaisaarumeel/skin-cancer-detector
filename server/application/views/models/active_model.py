from django.http import JsonResponse
from django.views import View

from ...decorators import admin_only
from ...models import ActiveModel


class GetActiveModel(View):
    @admin_only
    def get(self, request):
        try:
            # fetch active model through the ActiveModel table
            active_model = ActiveModel.objects.select_related("model").first()
            if not active_model:
                return JsonResponse({"err": "No active model found"}, status=404)

            active_model = active_model.model

            return JsonResponse(
                {
                    "version": active_model.version,
                    "created_at": active_model.created_at,
                    "hyperparameters": active_model.hyperparameters,
                }
            )

        except Exception as e:
            return JsonResponse({"err": str(e)}, status=500)
