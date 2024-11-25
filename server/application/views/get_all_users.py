from django.http import JsonResponse
from django.views import View
from ..models import Users
from ..decorators import admin_only


class GetAllUsers(View):
    @admin_only
    def get(self, request):
        try:
            # Get all users using the custom Users model
            users = Users.objects.all()

            # Prepare user data for response
            users_data = [
                {
                    "username": user.username,
                    "is_admin": user.is_admin,
                    "age": user.age,
                    "sex": user.sex,
                }
                for user in users
            ]

            return JsonResponse({"users": users_data}, status=200)

        except Exception as e:
            return JsonResponse(
                {"err": f"Error retrieving users: {str(e)}"}, status=500
            )
