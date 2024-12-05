from django.http import JsonResponse
from ..models import Requests
from django.views import View
from ..decorators import login_required
import base64


class GetRequestsByUsername(View):
    @login_required
    def get(self, request):
        try:
            user_requests = Requests.objects.filter(
                user__username=request.user.username
            ).order_by(
                "-created_at"
            )  # Order by the date created in descending order (latest first)

            # Map localization values to their corresponding display names from the choices
            def get_localization_display(localization):
                for choice_value, choice_label in Requests.LOCALIZATION_CHOICES:
                    if localization == choice_value:
                        return choice_label
                return localization  # Return the original value if not found

            request_data = [
                {
                    "request_id": req.request_id,
                    "created_at": req.created_at,
                    "probability": req.probability,
                    # Use the helper function to get the readable name for the localization
                    "localization": get_localization_display(req.localization),
                    "lesion_type": req.lesion_type,
                    "user": req.user.username,
                    "image": base64.b64encode(req.image).decode("utf-8"),
                    "model_version": req.model.version if req.model else None,
                }
                for req in user_requests
            ]

            return JsonResponse({"requests": request_data}, status=200)

        except Exception as e:
            return JsonResponse(
                {"err": f"Error retrieving the requests: {str(e)}"}, status=500
            )
