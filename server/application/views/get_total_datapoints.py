# Contributors:
# * Contributor: <amirpooya78@gmail.com>
from django.http import JsonResponse
from ..models import Data
from django.views import View
from ..decorators import admin_only


class GetTotalDataPoints(View):
    @admin_only  # Restrict access to admin users
    def get(self, request):
        try:
            # Count all datapoints in the DataPoint model
            total_data_points = Data.objects.using("db_images").count()

            # Return the count in a JSON response
            return JsonResponse(
                {"total_data_points": total_data_points},
                status=200,
            )

        except Exception as e:
            # Handle unexpected errors
            return JsonResponse(
                {"err": f"Error retrieving total data points: {str(e)}"}, status=500
            )
