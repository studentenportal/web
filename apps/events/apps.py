from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "apps.events"
    verbose_name = "Events"

    def ready(self):
        from apps.events import signals  # noqa: F401
