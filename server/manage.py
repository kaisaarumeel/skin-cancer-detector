#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import django



def main():
    global PREDICTION_JOBS
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skinscan.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Ensure that the setup is only run once
    # It should not be executed in the reloader
    # We should only run it if we pass runserver
    django.setup()
    if os.environ.get("RUN_MAIN") != "true" and "runserver" in sys.argv:
        from setup import setup
        setup.setup()


    # Start the server
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
