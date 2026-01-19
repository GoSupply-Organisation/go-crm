# Django Settings Configuration

## Structure

Go-CRM now uses environment-specific Django settings, following the pattern from iqed and testenv projects:

```
core/settings/
├── __init__.py          # Settings package documentation
├── base.py             # Common settings shared across all environments
├── local.py            # Development settings (default)
└── prod.py            # Production settings
```

## Usage

### Local Development (Default)
By default, Django uses `local.py` settings:

```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
```

### Production
To use production settings, set the environment variable:

```bash
DJANGO_SETTINGS_MODULE=core.settings.prod python manage.py runserver
```

### Switching Environments
```bash
# Local development
DJANGO_SETTINGS_MODULE=core.settings.local python manage.py runserver

# Production
DJANGO_SETTINGS_MODULE=core.settings.prod python manage.py runserver
```

## Configuration Files

### `base.py`
Contains settings shared across all environments:
- Basic Django configuration
- Apps and middleware
- Templates
- Authentication setup
- Celery configuration
- Base CORS/CSRF settings

### `local.py`
Development-specific overrides:
- `DEBUG = True`
- Debug Toolbar enabled
- Local PostgreSQL database
- Mailhog/local email backend
- Relaxed CORS settings (localhost)
- Cookie security disabled (no HTTPS)
- Celery eager execution for debugging

### `prod.py`
Production-specific overrides:
- `DEBUG = False`
- Security headers (HSTS, SSL redirect, etc.)
- Production database configuration
- Secure cookies (HTTPS only)
- Production email backend
- Logging configuration
- Cloud storage settings (if configured)

## Environment Variables

The settings use `python-decouple` to load environment variables from your existing `.env` file. Key variables include:

**Required:**
- `SECRET_KEY` - Django secret key
- `POSTGRES_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` - Database config
- `REDIS_HOST` - Redis/Celery connection string
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - Email credentials
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` - SMS credentials

**Production-only:**
- `ALLOWED_HOSTS` - Comma-separated list of allowed domains
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed frontend origins
- `CSRF_TRUSTED_ORIGINS` - Comma-separated list of trusted origins
- `STATIC_URL`, `MEDIA_URL` - CDN URLs (if using cloud storage)

## Migration from Old Settings

The old `settings.py` file is still present for reference. To fully migrate:

1. Review your existing `settings.py` for any custom configurations
2. Add missing settings to the appropriate environment file (`local.py` or `prod.py`)
3. Remove or rename the old `settings.py` once verified

## Benefits of This Pattern

- **Clear separation** between development and production
- **Security hardening** in production (SSL, cookies, headers)
- **Development tools** available locally (debug toolbar, eager tasks)
- **Environment-specific** database, email, and CORS configurations
- **Easy switching** between environments via environment variables
- **Consistent pattern** with your other Django projects