from django.http import JsonResponse
from django.views import View
from django.db import transaction

from time import time
from ...decorators import admin_only
from ...models import ActiveModel
from ...models import Model


class SwapModel(View):
    @admin_only
    def post(self, request, *args, **kwargs):
        try:
            version = kwargs.get("version")

            # groups all db operations within this block in a single operation
            # if exception occurs, all db queries are rolled back
            with transaction.atomic():
                # find requested model based on version query parameter
                new_model = Model.objects.get(version=version)

                # if entry exists, update it to reference new model
                # if table is empty, create the row
                ActiveModel.objects.update_or_create(
                    id=1,
                    defaults={
                        "model": new_model,
                        "updated_at": int(time()),
                    },
                )

            return JsonResponse(
                {"message": f"Active model changed to version {new_model.version}"}
            )

        except Model.DoesNotExist:
            return JsonResponse({"err": "Model not found"}, status=404)
        except Exception as e:
            return JsonResponse({"err": f"Failed to swap models: {str(e)}"}, status=500)
