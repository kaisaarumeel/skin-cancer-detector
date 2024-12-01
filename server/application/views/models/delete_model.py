from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist

from ...decorators import admin_only
from ...models import Model


class DeleteModel(View):
    @admin_only
    def delete(self, request, *args, **kwargs):
        try:
            version = kwargs.get("version")

            # fetch and delete model using provided version
            model = Model.objects.get(version=version)
            model.delete()
            
            return JsonResponse({"message": f"Model version {version}.0 deleted successfully"}, status=204)
        
        except ObjectDoesNotExist:
            return JsonResponse({"err": f"Model version {version}.0 does not exist"}, status=404)
        except Exception as e:
            return JsonResponse({"err": f"An unexpected error occurred {str(e)}"}, status=500)
            
