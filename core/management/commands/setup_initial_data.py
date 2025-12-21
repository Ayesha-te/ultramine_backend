from django.core.management.base import BaseCommand
from core.models import MiningPackage, ROISetting, ReinvestSetting
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up initial data (packages, settings)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up initial data...'))
        
        packages_data = [
            {'name': 'Starter Lite', 'price': Decimal('500'), 'daily_earning': Decimal('5'), 'duration_days': 30},
            {'name': 'Basic', 'price': Decimal('1000'), 'daily_earning': Decimal('10'), 'duration_days': 30},
            {'name': 'Starter', 'price': Decimal('2500'), 'daily_earning': Decimal('25'), 'duration_days': 30},
            {'name': 'Mini Pro', 'price': Decimal('5000'), 'daily_earning': Decimal('50'), 'duration_days': 30},
            {'name': 'Standard', 'price': Decimal('10000'), 'daily_earning': Decimal('100'), 'duration_days': 30},
            {'name': 'Advance', 'price': Decimal('20000'), 'daily_earning': Decimal('200'), 'duration_days': 30},
            {'name': 'Premium', 'price': Decimal('30000'), 'daily_earning': Decimal('300'), 'duration_days': 30},
            {'name': 'Gold', 'price': Decimal('50000'), 'daily_earning': Decimal('500'), 'duration_days': 30},
            {'name': 'Elite', 'price': Decimal('75000'), 'daily_earning': Decimal('750'), 'duration_days': 30},
            {'name': 'Diamond', 'price': Decimal('100000'), 'daily_earning': Decimal('1000'), 'duration_days': 30},
            {'name': 'Master', 'price': Decimal('150000'), 'daily_earning': Decimal('1500'), 'duration_days': 30},
            {'name': 'Royal', 'price': Decimal('200000'), 'daily_earning': Decimal('2000'), 'duration_days': 30},
            {'name': 'VIP', 'price': Decimal('250000'), 'daily_earning': Decimal('2500'), 'duration_days': 30},
        ]
        
        for pkg_data in packages_data:
            pkg, created = MiningPackage.objects.get_or_create(
                name=pkg_data['name'],
                defaults=pkg_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created package: {pkg.name}'))
            else:
                self.stdout.write(f'Package {pkg.name} already exists')
        
        roi, created = ROISetting.objects.get_or_create(
            id=1,
            defaults={
                'min_percentage': Decimal('0.8'),
                'max_percentage': Decimal('1.2'),
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created ROI Setting'))
        else:
            self.stdout.write('ROI Setting already exists')
        
        reinvest, created = ReinvestSetting.objects.get_or_create(
            id=1,
            defaults={
                'percentage': Decimal('30'),
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Reinvest Setting'))
        else:
            self.stdout.write('Reinvest Setting already exists')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed!'))
