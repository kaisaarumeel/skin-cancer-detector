from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.test.sqlite3",
    },
    "data": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "data.sqlite3"},
}

# Disable any unnecessary middleware
MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE
    if not middleware.startswith("django.middleware.security")
    and not middleware.startswith("django.middleware.csrf")
]
