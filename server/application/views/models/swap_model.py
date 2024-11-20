from django.http import JsonResponse
from django.views import View

from ...decorators import admin_only
from ...models import Model


class SwapModel(View):
    @admin_only
    def put(self, request, *args, **kwargs):
        try:
            # find requested model based on model_id query parameter
            model_id = kwargs.get("model_id")
            new_model = Model.objects.get(model_id=model_id)

            # deactivate currently active model(s)
            Model.objects.filter(status="active").update(status="archived")

            # activate the new model
            new_model.status = "active"
            new_model.save()

            return JsonResponse(
                {
                    "message": f"Active model swapped to model {new_model.model_id} version {new_model.version}"
                }
            )

        except Model.DoesNotExist:
            return JsonResponse({"error": "Model not found."}, status=404)
        except Exception as e:
            return JsonResponse(
                {"error": f"Failed to swap models: {str(e)}"}, status=500
            )