from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def run_daily_earnings_task():
    try:
        logger.info("Running daily earnings calculation...")
        call_command('calculate_daily_earnings')
        logger.info("Daily earnings calculation completed successfully")
    except Exception as e:
        logger.error(f"Error in daily earnings task: {str(e)}")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            run_daily_earnings_task,
            'cron',
            hour=0,
            minute=0,
            id='daily_earnings_job',
            name='Calculate daily earnings for all users',
            replace_existing=True
        )
        scheduler.start()
        logger.info("Earnings scheduler started - runs daily at 00:00 UTC")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Earnings scheduler stopped")
