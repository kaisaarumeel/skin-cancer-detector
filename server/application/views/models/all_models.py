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

        models_data = [
            {
                "model_id": model.model_id,
                "created_at": model.created_at,
                "version": model.version,
                "weights": base64.b64encode(model.weights).decode(
                    "utf-8"
                ),  # convert to base64 string, which is JSON-serializable
                "status": model.status,
                "input_shape": model.input_shape,
                "num_filters": model.num_filters,
                "kernel_size": model.kernel_size,
                "pool_size": model.pool_size,
                "dropout_rate": model.dropout_rate,
                "dense_units": model.dense_units,
                "activation_function": model.activation_function,
                "optimizer": model.optimizer,
                "loss_function": model.loss_function,
                "metrics": model.metrics,
                "batch_size": model.batch_size,
                "epochs": model.epochs,
            }
            for model in models
        ]

        return JsonResponse({"models": models_data}, status=200)
