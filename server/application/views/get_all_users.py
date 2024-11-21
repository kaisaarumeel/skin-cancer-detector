from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views import View


# Creating a class-based view for getting all users
class GetAllUsersView(View):
    def get(self, request):
        try:
            # Getting all users using Django's get_user_model
            users = get_user_model().objects.all()

            # Preparing a list of user data to return
            users_data = [
                {
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
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
