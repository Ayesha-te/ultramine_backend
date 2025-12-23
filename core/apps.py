from django.apps import AppConfig
import os
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    name = 'core'
    
    def ready(self):
        from django.core.management import call_command
        import sys
        
        if os.environ.get('SKIP_SCHEDULER_STARTUP') == 'true':
            logger.info("Skipping scheduler startup (SKIP_SCHEDULER_STARTUP=true)")
            return
        
        if 'migrate' in sys.argv or 'collectstatic' in sys.argv:
            logger.info("Skipping scheduler startup during migration/collectstatic")
            return
        
        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.warning(f"Could not start scheduler during app initialization: {str(e)}")
