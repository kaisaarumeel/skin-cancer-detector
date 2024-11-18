from django.http import JsonResponse
from django.views import View

from ...models import Model

class swapModel(View):
    def put(self, request):
        try:
            new_model = Model.objects.get(model_id=model_id)
            
            # Deactivate the current active model
            Model.objects.filter(status="active").update(status="archived")
            
            # Activate the new model
            new_model.status = "active"
            new_model.save()
            
            return JsonResponse({"message": f"Active model switched to version {new_model.version}"})
        except Model.DoesNotExist:
            return JsonResponse({"error": "Model not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Failed to swap models: {str(e)}"}, status=500)