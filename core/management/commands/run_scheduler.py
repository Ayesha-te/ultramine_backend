from django.core.management.base import BaseCommand
from core.scheduler import start_scheduler, stop_scheduler
import time
import signal
import sys


class Command(BaseCommand):
    help = 'Run the background scheduler for earnings calculation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run in test mode (executes immediately)',
        )

    def handle(self, *args, **options):
        if options['test']:
            self.stdout.write(self.style.SUCCESS('Running earnings calculation in test mode...'))
            from core.management.commands.calculate_daily_earnings import Command as EarningsCommand
            cmd = EarningsCommand()
            cmd.handle()
            return

        self.stdout.write(self.style.SUCCESS('Starting background scheduler...'))
        self.stdout.write('Press Ctrl+C to stop')

        start_scheduler()

        def signal_handler(sig, frame):
            self.stdout.write('\nShutting down scheduler...')
            stop_scheduler()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_scheduler()
