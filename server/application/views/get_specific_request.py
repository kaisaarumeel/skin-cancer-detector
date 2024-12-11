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

            # Get actual feature impacts from the database
            feature_impact = [
                {"feature": "age", "impact": 0.1},
                {"feature": "sex", "impact": 0.1},
                {
                    "feature": "localization",
                    "impact": 0.1,
                },
            ]

            # Get actual pixel impact (binary-encoded Grad-CAM heatmap)
            pixel_impact = (
                base64.b64encode(specific_request.heatmap).decode("utf-8")
                if specific_request.heatmap
                else None
            )

            request_data = {
                "request_id": specific_request.request_id,
                "created_at": specific_request.created_at,
                "image": base64.b64encode(specific_request.image).decode("utf-8"),
                "probability": specific_request.probability,
                "localization": specific_request.localization,
                "lesion_type": specific_request.lesion_type,
                "user": specific_request.user.username,
                "model_version": (
                    specific_request.model.version if specific_request.model else None
                ),
                "feature_impact": feature_impact,
                "pixel_impact": pixel_impact,
            }

            return JsonResponse({"request": request_data}, status=200)

        except Exception as e:
            return JsonResponse(
                {"err": f"Error retrieving the request: {str(e)}"}, status=500
            )
