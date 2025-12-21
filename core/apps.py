from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    
    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()
