
import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project.

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the project root.

# BASE_DIR points to src/, so BASE_DIR.parent is the project root.

load_dotenv(BASE_DIR.parent / ".env")

# Security settings

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["127.0.0.1"]

# Application definition

INSTALLED_APPS = [
"django.contrib.admin",
"django.contrib.auth",
"django.contrib.contenttypes",
"django.contrib.sessions",
"django.contrib.messages",
"django.contrib.staticfiles",
"rest_framework",
"population",
]

MIDDLEWARE = [
"django.middleware.security.SecurityMiddleware",
"django.contrib.sessions.middleware.SessionMiddleware",
"django.middleware.common.CommonMiddleware",
"django.middleware.csrf.CsrfViewMiddleware",
"django.contrib.auth.middleware.AuthenticationMiddleware",
"django.contrib.messages.middleware.MessageMiddleware",
"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
{
"BACKEND": "django.template.backends.django.DjangoTemplates",
"DIRS": [],
"APP_DIRS": True,
"OPTIONS": {
"context_processors": [
"django.template.context_processors.request",
"django.contrib.auth.context_processors.auth",
"django.contrib.messages.context_processors.messages",
],
},
},
]

WSGI_APPLICATION = "config.wsgi.application"

# Database: PostgreSQL

DATABASES = {
"default": {
"ENGINE": "django.db.backends.postgresql",
"NAME": os.environ["DB_NAME"],
"USER": os.environ["DB_USER"],
"PASSWORD": os.environ["DB_PASSWORD"],
"HOST": os.environ.get("DB_HOST", "127.0.0.1"),
"PORT": os.environ.get("DB_PORT", "5432"),
}
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
{
"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
},
{
"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
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

USE_I18N = True

USE_TZ = True

# Static files

STATIC_URL = "static/"

# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
  "DEFAULT_PAGINATION_CLASS":(
    "rest_framework.pagination.PageNumberPagination"
  ),
  "PAGE_SIZE":100,
}