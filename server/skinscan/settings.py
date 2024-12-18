import os
from pathlib import Path

from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parents[2]

# Load environment variables
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.getenv("SECRET_KEY"))

# Ensure SECRET_KEY is set, or raise an error
if SECRET_KEY == "None":
    raise ValueError("The SECRET_KEY environment variable is not set.")

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv("DEBUG") == "False":
    DEBUG = False
else:
    DEBUG = True
print(f"DEBUG is set to {DEBUG}")

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "application",
]

# Custom User Model for authentication
AUTH_USER_MODEL = "application.Users"

# Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",   # Disable CORS until we have a domain
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "skinscan.urls"
WSGI_APPLICATION = "wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_app.sqlite3",
    },
    "db_images": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_images.sqlite3",
    },
}

# Path to database router that restricts migrations to the two databases
DATABASE_ROUTERS = ["utils.db_router.MigrationRouter"]

# List of models that should only be added as tables to the image DB
# The database router will restrict migrations to the DBs using this list
# NOTE: Django handles model names as lowercase hence listed names should be lowercase
# Source: https://github.com/django/django/blob/main/django/db/models/options.py#L179
IMAGE_DB_MODELS = [
    "data",
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Session settings
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 86400  # Session expires after 24 hours

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://164.92.176.222", # Production - public IP address
]
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_SECURE = False  # Only sent over HTTPS
CSRF_COOKIE_HTTPONLY = False  # Cookie is accessible to JavaScript in client
SESSION_COOKIE_SECURE = False

# Security settings (for production)
if not DEBUG:
    # Enable these if we setup a domain name + HTTPS
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
    "http://164.92.176.222", # Production - public IP address
]
CORS_ALLOW_CREDENTIALS = True

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
