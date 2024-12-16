import base64
from django.http import JsonResponse
from django.views import View
from ..decorators import login_required
from ..models import Requests


class GetSpecificRequest(View):
    @login_required
    def get(self, request, request_id):
        try:
            specific_request = Requests.objects.filter(request_id=request_id).first()

            if not specific_request:
                return JsonResponse({"err": "Request not found"}, status=404)

            if (
                not request.user.is_admin
                and specific_request.user.username != request.user.username
            ):
                return JsonResponse({"err": "access denied"}, status=403)

            # Encode the visualized image as base64
            pixel_impact_visualized = (
                base64.b64encode(specific_request.heatmap).decode("utf-8")
                if specific_request.heatmap
                else None
            )

            # Map lesion type values to their corresponding display names
            def get_lesion_display(lesion_type):
                for choice_value, choice_label in Requests.LESION_TYPE_CHOICES:
                    if lesion_type == choice_value:
                        return choice_label
                return lesion_type  # Return the original value if not found

            request_data = {
                "request_id": specific_request.request_id,
                "created_at": specific_request.created_at,
                "image": base64.b64encode(specific_request.image).decode("utf-8"),
                "probability": specific_request.probability,
                "localization": specific_request.localization,
                "lesion_type": get_lesion_display(specific_request.lesion_type),
                "user": specific_request.user.username,
                "model_version": (
                    specific_request.model if specific_request.model else None
                ),
                "feature_impact": specific_request.feature_impact,
                "pixel_impact_visualized": pixel_impact_visualized,
            }

            return JsonResponse({"request": request_data}, status=200)

        except Exception as e:
            print(e)
            return JsonResponse(
                {"err": f"Error retrieving the request: {str(e)}"}, status=500
            )
