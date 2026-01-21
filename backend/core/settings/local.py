"""
Django settings for core project - Local Development Environment

Development-specific overrides for base.py.
Includes debug tools, local services, and relaxed security.
WARNING: These settings are NOT suitable for production use.
"""

from .base import *
from decouple import config

# Debug Configuration
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Development Middleware
MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

# Development Apps
INSTALLED_APPS += [
    "debug_toolbar",
]

# Debug Toolbar Configuration
def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

# Database Configuration (Local)
DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql",
        'NAME': config("POSTGRES_NAME"),
        'USER': config("POSTGRES_USER"),
        'PASSWORD': config("POSTGRES_PASSWORD"),
        'HOST': config("POSTGRES_HOST"),
        'PORT': config("POSTGRES_PORT"),
    }
}

# Email Configuration (Local)
# Use console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery Configuration (Local)
# Execute tasks synchronously for easier debugging
CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=True, cast=bool)
CELERY_INCLUDE_BUILTINS = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# CORS Configuration (Local)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# CSRF Configuration (Local)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Cookie configuration for local development (no HTTPS)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
