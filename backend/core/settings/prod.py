"""
Django settings for core project - Production Environment

Production-specific overrides for base.py.
Includes security hardening, production services, and monitoring.
"""

from .base import *
from decouple import config

# Security & Allowed Hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(", ")

# Trust proxy headers from nginx
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Security Headers
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie Security (HTTPS Only)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_DOMAIN = None
SESSION_COOKIE_DOMAIN = None

# Database Configuration (Production)
DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql",
        'NAME': config("POSTGRES_NAME"),
        'USER': config("POSTGRES_USER"),
        'PASSWORD': config("POSTGRES_PASSWORD"),
        'HOST': config("POSTGRES_HOST"),
        'PORT': config("POSTGRES_PORT"),
        'OPTIONS': {"sslmode": "prefer"},
        'CONN_MAX_AGE': 30,
        'CONN_HEALTH_CHECKS': True,
    }
}

# CORS Configuration (Production)
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in config('CORS_ALLOWED_ORIGINS', default='').split(",")
    if origin.strip()
]

# CSRF Configuration (Production)
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in config('CSRF_TRUSTED_ORIGINS', default='').split(",")
    if origin.strip()
]

# Static Files (Production)
# You may want to use CDN or cloud storage (S3, Azure Blob, etc.)
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media Files (Production)
# You may want to use cloud storage for media files
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Logging Configuration (Production)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
