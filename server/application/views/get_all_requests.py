from django.http import JsonResponse
from ..models import Requests
from django.views import View


# Creating a class-based view for getting all requests
class GetAllRequests(View):
    def get(self, request):
        try:
            # Fetching all requests from the Requests model
            requests = Requests.objects.all()

            # Preparing the list of requests to send in the response
            request_data = [
                {
                    "request_id": req.request_id,
                    "created_at": req.created_at,
                    "probability": req.probability,
                    "localization": req.localization,
                    "lesion_type": req.lesion_type,
                    "user": req.user.username,
                    "model_version": (
                        req.model.version if req.model else None
                    ),  # Assuming model is related to request
                }
                for req in requests
            ]

            return JsonResponse({"requests": request_data}, status=200)

        except Exception as e:
            return JsonResponse(
                {"err": f"Error retrieving requests: {str(e)}"}, status=500
            )
