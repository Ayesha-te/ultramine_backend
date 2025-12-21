from django.core.management.base import BaseCommand
from core.services import EarningService


class Command(BaseCommand):
    help = 'Calculate daily earnings for all users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting daily earnings calculation...'))
        
        try:
            EarningService.calculate_daily_earnings()
            self.stdout.write(self.style.SUCCESS('Daily earnings calculated successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error calculating daily earnings: {str(e)}'))
        
        try:
            EarningService.process_referral_earnings()
            self.stdout.write(self.style.SUCCESS('Referral earnings processed successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing referral earnings: {str(e)}'))
