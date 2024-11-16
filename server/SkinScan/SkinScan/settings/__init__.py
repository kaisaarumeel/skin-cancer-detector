import os

# Get environment variable
env = str(os.getenv('DJANGO_ENV'))

# Import correct settings file
if env == 'development':
    from .development import *
else:
    from .production import *
