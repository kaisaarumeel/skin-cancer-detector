import base64
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
                "weights": base64.b64encode(active_model.weights).decode('utf-8'),  # convert to base64 string, which is JSON-serializable
                "status": active_model.status,
                "input_shape": active_model.input_shape,
                "num_filters": active_model.num_filters,
                "kernel_size": active_model.kernel_size,
                "pool_size": active_model.pool_size,
                "dropout_rate": active_model.dropout_rate,
                "dense_units": active_model.dense_units,
                "activation_function": active_model.activation_function,
                "optimizer": active_model.optimizer,
                "loss_function": active_model.loss_function,
                "metrics": active_model.metrics,
                "batch_size": active_model.batch_size,
                "epochs": active_model.epochs,
            })
        
        except Model.DoesNotExist:
            return JsonResponse({"err": "No active model found"}, status=404)
