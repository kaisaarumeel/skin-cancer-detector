"""
URL configuration for SkinScan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from .views.change_password import ChangePassword
from .views.login import Login
from .views.register import Register
from .views.create_request import CreateRequest
from .views.add_data import AddData
from .views.models.all_models import GetAllModels
from .views.models.active_model import GetActiveModel
from .views.models.swap_model import SwapModel
from .views.models.delete_model import DeleteModel
from .views.get_all_requests import GetAllRequests
from .views.get_all_users import GetAllUsers
from .views.jobs.retrain import Retrain
from .views.is_logged_in import IsLoggedIn
from .views.logout import Logout
from .views.is_admin import IsAdmin
from .views.get_specific_request import GetSpecificRequest
from .views.get_requests_by_username import GetRequestsByUsername
from .views.delete_user import DeleteUser
from .views.get_number_of_datapoints import GetTotalDataPoints


urlpatterns = [
    path("login/", Login.as_view(), name="api-login"),
    path("register/", Register.as_view(), name="api-register"),
    path("change-password/", ChangePassword.as_view(), name="api-change-password"),
    path("create-request/", CreateRequest.as_view(), name="api-create-request"),
    path("add-data/", AddData.as_view(), name="add-data"),
    path("models/all-models/", GetAllModels.as_view(), name="api-all-models"),
    path("models/active-model/", GetActiveModel.as_view(), name="api-active-model"),
    path(
        "models/swap-model/<int:version>/", SwapModel.as_view(), name="api-swap-model"
    ),
    path(
        "models/delete-model/<int:version>/",
        DeleteModel.as_view(),
        name="api-delete-model",
    ),
    path("get-all-requests/", GetAllRequests.as_view(), name="api-get-all-requests"),
    path("get-all-users/", GetAllUsers.as_view(), name="api-get-all-users"),
    path("retrain/", Retrain.as_view(), name="api-retrain-model"),
    path("is_logged_in/", IsLoggedIn.as_view(), name="api-is-logged-in"),
    path("logout/", Logout.as_view(), name="api-logout"),
    path("is_admin/", IsAdmin.as_view(), name="api-is-admin"),
    path(
        "get-specific-request/<int:request_id>/",
        GetSpecificRequest.as_view(),
        name="api-get-specific-request",
    ),
    path(
        "get-requests-by-username/",
        GetRequestsByUsername.as_view(),
        name="api-get-requests-by-username",
    ),
    path("delete-user/<str:username>/", DeleteUser.as_view(), name="api-delete-user"),
    path(
        "get-total-datapoints/",
        GetTotalDataPoints.as_view(),
        name="api-get-total-datapoints",
    ),
]
