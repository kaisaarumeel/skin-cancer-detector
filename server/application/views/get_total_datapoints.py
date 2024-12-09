from django.http import JsonResponse
from ..models import Data  # Replace with your actual model name
from django.views import View
from ..decorators import admin_only


class GetTotalDataPoints(View):
    @admin_only  # Restrict access to admin users
    def get(self, request):
        try:
            # Count all datapoints in the DataPoint model
            total_data_points = Data.objects.count()

            # 20 percent of total data points are reserved for tests
            test_total = int(total_data_points * 0.2)
            train_total = total_data_points - test_total

            # Return the count in a JSON response
            return JsonResponse(
                {
                    "total_data_points": total_data_points,
                    "test_total": test_total,
                    "train_total": train_total,
                },
                status=200,
            )

        except Exception as e:
            # Handle unexpected errors
            return JsonResponse(
                {"err": f"Error retrieving total data points: {str(e)}"}, status=500
            )
