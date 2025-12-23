from django.apps import AppConfig
import os
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    name = 'core'
    
    def ready(self):
        logger.info("Core app initialized - scheduler disabled during startup")
