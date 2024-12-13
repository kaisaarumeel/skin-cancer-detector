from django.contrib.auth.hashers import make_password

from ..application.models import Users


def create_admin_user(username, password, age, sex):
    try:
        Users.objects.using("default").get(username=username)
    except Users.DoesNotExist:
        try:
            Users.objects.using("default").create(
                username=username,
                password=make_password(password),
                age=age,
                sex=sex,
                is_admin=True,
                is_active=True,
            )
        except Exception as e:
            print(e)
