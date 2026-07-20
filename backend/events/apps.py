from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "events"

    def ready(self):
        from .services.cache_service import load_cache

        try:
            load_cache()
        except Exception:
            pass