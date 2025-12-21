import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import WithdrawalTaxSetting

existing = WithdrawalTaxSetting.objects.filter(is_active=True).first()
if not existing:
    setting = WithdrawalTaxSetting.objects.create(percentage=20, is_active=True)
    print(f"Created initial WithdrawalTaxSetting with ID {setting.id}")
else:
    print(f"WithdrawalTaxSetting already exists with ID {existing.id}, percentage: {existing.percentage}%")
