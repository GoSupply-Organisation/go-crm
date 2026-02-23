"""Django app configuration for the core module."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Django app configuration for the core module.

    This configuration ensures that Celery task autodiscovery runs exactly
    once during application startup by moving the autodiscover_tasks() call
    from module-level execution to the ready() method.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """Called when Django starts - ensure Celery autodiscover runs once."""
        from .celery import app as celery_app

        # Autodiscover Celery tasks from all installed apps
        celery_app.autodiscover_tasks()
