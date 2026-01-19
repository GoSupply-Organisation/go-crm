"""
Django settings for core project - Base Configuration

Shared settings across all environments (local, production).
Environment-specific settings override these in their respective files.
"""

from pathlib import Path
from decouple import config
import os
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Core Configuration
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = []


# Application Definition
INSTALLED_APPS = [
    # Django Initialisation Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_twilio',
    "sms",
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'ninja',
    'corsheaders',
    "anymail",

    # Created Apps
    "contacts",
    "super_researcher",
    "todo",
    "apex",
    "user",
    "communications",
]


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static Files
STATIC_URL = 'static/'


# Default Primary Key Field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email Configuration - Will be overridden in local.py and prod.py
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

ANYMAIL = {
    "MAILGUN_API_KEY": config('MAILGUN_API_KEY'),
}

# SMS Configuration
SMS_BACKEND = 'sms.backends.twilio.SmsBackend'
TWILIO_ACCOUNT = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH = config('TWILIO_AUTH_TOKEN')


# Celery Configuration
CELERY_TIMEZONE = config('CELERY_TIMEZONE', default='Australia/Sydney')
CELERY_BROKER_URL = config('REDIS_HOST')
CELERY_BEAT_SCHEDULE = {
    "RunSuperResearcher": {
        "task": "super_researcher.tasks.periodic_lead_generation",
        "schedule": crontab(minute=5),  # Run every 5 minutes
    },
}


# CORS Configuration - Will be overridden in local.py and prod.py
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_CREDENTIALS = True


# CSRF Configuration - Will be overridden in local.py and prod.py
CSRF_TRUSTED_ORIGINS = []


# Authentication
LOGIN_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'user.CustomUser'
