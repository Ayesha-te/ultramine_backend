from django.apps import AppConfig
import os
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    name = 'core'
    
    def ready(self):
        import sys
        
        if 'runserver' not in sys.argv and 'RUN_SCHEDULER' not in os.environ:
            logger.info("Scheduler initialization disabled during deployment")
            return
        
        if os.environ.get('RUN_SCHEDULER') == 'false':
            logger.info("Skipping scheduler (RUN_SCHEDULER=false)")
            return
        
        if 'migrate' in sys.argv or 'collectstatic' in sys.argv or 'gunicorn' in sys.argv:
            logger.info("Skipping scheduler during deployment commands")
            return
        
        try:
            from .scheduler import start_scheduler
            logger.info("Attempting to start scheduler...")
            start_scheduler()
        except Exception as e:
            logger.warning(f"Could not start scheduler: {str(e)}")
