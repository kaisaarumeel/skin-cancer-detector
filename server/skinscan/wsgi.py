"""
WSGI config for SkinScan project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from server.setup.setup import setup
from server.application.predictions.prediction_manager import start_prediction_manager

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.skinscan.settings")

setup()
start_prediction_manager()

application = get_wsgi_application()
