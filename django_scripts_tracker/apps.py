from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ScriptsTrackerConfig(AppConfig):
    name = 'django_scripts_tracker'
    verbose_name = "Django Scripts Tracker"

    def ready(self):
        from django_scripts_tracker.core_tracker import check_scripts_signal_handler
        post_migrate.connect(check_scripts_signal_handler, sender=self)
