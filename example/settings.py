import logging
import os

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
MEDIA_DIR = os.path.join(PROJECT_DIR, "/media")
STATIC_DIR = os.path.join(PROJECT_DIR, "/static")
TEMPLATE_DIR = os.path.join(PROJECT_DIR, "templates")

DEBUG = True

STATIC_URL = "/static/"
STATIC_ROOT = STATIC_DIR

MEDIA_URL = "/media/"
MEDIA_ROOT = MEDIA_DIR

SECRET_KEY = "secret_key"

ADMINS = ()

ALLOWED_HOSTS = ()

CORS_ALLOWED_ORIGINS = [
    "https://127.0.0.1",
]

SITE_ID = 1

CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "example.polls",
    "django_admin_tabs",
]

LANGUAGE_CODE = "en"

LANGUAGES = (("en", _("English")),)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            TEMPLATE_DIR,
        ],
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

LOGIN_REDIRECT_URL = "/"

WSGI_APPLICATION = "example.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "sqlite.db",
    }
}


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

TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

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
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "example": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
