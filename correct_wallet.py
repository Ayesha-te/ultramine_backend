import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import DailyEarning, Wallet
from django.contrib.auth import get_user_model
from django.db.models import Sum
from decimal import Decimal

User = get_user_model()
user = User.objects.get(email='farah@gmail.com')
wallet = user.wallet

mining = DailyEarning.objects.filter(user=user, earning_type='mining').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
roi = DailyEarning.objects.filter(user=user, earning_type='roi').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
referral = DailyEarning.objects.filter(user=user, earning_type='referral').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
reinvest = DailyEarning.objects.filter(user=user, earning_type='reinvest').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

print("CORRECTING WALLET FROM DATABASE:")
print("=" * 60)
print(f"Mining earnings (DB):     Rs{mining}")
print(f"ROI earnings (DB):        Rs{roi}")
print(f"Referral earnings (DB):   Rs{referral}")
print(f"Reinvest (DB):            Rs{reinvest}")

balance_from_earnings = Decimal('700') + mining + roi + referral

print(f"\nBase (deposits + bonus):  Rs700.00")
print(f"Total earnings:            Rs{mining + roi + referral}")
print(f"(Reinvest is tracked separately, already included above)")
print(f"Expected balance:          Rs{balance_from_earnings}")

wallet.mining_income = mining
wallet.roi_earnings = roi
wallet.referral_earnings = referral
wallet.balance = balance_from_earnings
wallet.save()

print(f"\nWallet CORRECTED:")
print(f"  Mining income: Rs{wallet.mining_income}")
print(f"  ROI earnings:  Rs{wallet.roi_earnings}")
print(f"  Referral:      Rs{wallet.referral_earnings}")
print(f"  Balance:       Rs{wallet.balance}")
