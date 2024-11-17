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

urlpatterns = [
    path('login/', Login.as_view(), name='api-login'),
    path('register/', Register.as_view(), name='api-register'),
    path('change-password/', ChangePassword.as_view(), name='api-change-password'),
]
