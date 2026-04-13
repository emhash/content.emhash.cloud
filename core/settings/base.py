import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --------- CONFIGURATIONS  ----------=======
from .configurations.logging import *
from .configurations.security import *
from .configurations.celery import *
# -----------========= ---------------=======


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "https://api.patchping.com")

# ---------------- System Apps -----------------
SYSTEM_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

]
# only if debug toolbar is enabled --->>
if globals().get('ENABLE_DEBUG_TOOLBAR', False):
    SYSTEM_APPS.append('debug_toolbar')
# ---------------- System Apps -----------------


# ----------- Third party apps ---------------
THIRD_PARTY_APPS = [
    "django_extensions",
    "tinymce",

]

#----------- Local apps ---------------
LOCAL_APPS = [
    "apps.command",
    "apps.accounts",
    "apps.content"
]


INSTALLED_APPS = SYSTEM_APPS + THIRD_PARTY_APPS + LOCAL_APPS



MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# only if debug toolbar is enabled --->>
if globals().get('ENABLE_DEBUG_TOOLBAR', False):
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')


ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "core.wsgi.application"

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
TAGGIT_CASE_INSENSITIVE = True

AUTH_USER_MODEL = "accounts.User"

# ----------- CREDENTIALS ---------------=======
from .credentials.mail import *


# ----------- VERSION INFORMATION ---------------
VERSION = os.getenv("APP_VERSION", "1.0.0")


TINYMCE_DEFAULT_CONFIG = {
    "height": 320,
    "menubar": True,
    "plugins": "advlist autolink lists link image media table code fullscreen help wordcount",
    "toolbar": (
        "undo redo | blocks | bold italic underline | alignleft aligncenter alignright | "
        "bullist numlist outdent indent | link image media | code fullscreen"
    ),
    "automatic_uploads": True,
    "images_upload_url": "/api/tinymce-upload/",
    "images_upload_credentials": True,
}