"""
Settings package for core Django project.

This package provides environment-specific Django settings:
- base.py: Common settings shared across all environments
- local.py: Development settings (default)
- prod.py: Production settings

To use a specific environment:
- Local (default): DJANGO_SETTINGS_MODULE=core.settings.local python manage.py runserver
- Production: DJANGO_SETTINGS_MODULE=core.settings.prod python manage.py runserver
"""
