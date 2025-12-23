from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
import logging
import os

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(daemon=True)
_scheduler_started = False

def run_daily_earnings_task():
    try:
        logger.info("Running daily earnings calculation...")
        call_command('calculate_daily_earnings')
        logger.info("Daily earnings calculation completed successfully")
    except Exception as e:
        logger.error(f"Error in daily earnings task: {str(e)}", exc_info=True)

def start_scheduler():
    global _scheduler_started
    
    if _scheduler_started or scheduler.running:
        logger.debug("Scheduler already running or initialized")
        return
    
    if os.environ.get('RUN_SCHEDULER') == 'false':
        logger.info("Scheduler disabled via RUN_SCHEDULER environment variable")
        return
    
    try:
        logger.info("Initializing scheduler...")
        if 'daily_earnings_job' not in [job.id for job in scheduler.get_jobs()]:
            scheduler.add_job(
                run_daily_earnings_task,
                'cron',
                hour=0,
                minute=0,
                id='daily_earnings_job',
                name='Calculate daily earnings for all users',
                replace_existing=True,
                misfire_grace_time=300,
                max_instances=1
            )
            logger.info("Daily earnings job added to scheduler")
        
        if not scheduler.running:
            logger.info("Starting background scheduler...")
            scheduler.start()
            logger.info("Scheduler started successfully")
        
        _scheduler_started = True
        logger.info("Earnings scheduler ready - runs daily at 00:00 UTC")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}", exc_info=True)
        _scheduler_started = False

def stop_scheduler():
    if scheduler.running:
        try:
            scheduler.shutdown(wait=False)
            logger.info("Earnings scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}", exc_info=True)
