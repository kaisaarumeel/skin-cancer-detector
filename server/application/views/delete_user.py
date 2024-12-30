# Contributors:
# * Contributor: <kaisa.arumeel@gmail.com>
from django.http import JsonResponse
from django.views import View
from ..models import Users
from django.core.exceptions import ObjectDoesNotExist


class DeleteUser(View):
    def delete(self, request, username):
        # Check if the user is authenticated and is an admin
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse(
                {"err": "Unauthorized. Admin access required."}, status=403
            )

        try:
            # Check if the user exists
            user_to_delete = Users.objects.get(username=username)

            # Prevent the admin from deleting themselves
            if user_to_delete == request.user:
                return JsonResponse(
                    {"err": "Admin cannot delete themselves."}, status=400
                )

            # Delete the user
            user_to_delete.delete()

            return JsonResponse({"msg": "User deleted successfully."}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({"err": "User not found."}, status=404)
