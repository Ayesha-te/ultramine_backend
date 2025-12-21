import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Deposit, DailyEarning, Wallet, Transaction, ROISetting, ReinvestSetting
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, timezone, timedelta

User = get_user_model()
user = User.objects.get(email='farah@gmail.com')
wallet = user.wallet
deposit = Deposit.objects.get(user=user)

print("=" * 70)
print("BACKFILL MISSING DAILY EARNINGS")
print("=" * 70)

print(f"\nDeposit approved: {deposit.approved_at.date()}")

roi_setting = ROISetting.objects.filter(is_active=True).first()
roi_percentage = (roi_setting.min_percentage + roi_setting.max_percentage) / 2 if roi_setting else Decimal('1.0')
print(f"ROI percentage: {roi_percentage}%")

reinvest_setting = ReinvestSetting.objects.filter(is_active=True).first()
reinvest_pct = reinvest_setting.percentage if reinvest_setting else Decimal('0')
print(f"Reinvest percentage: {reinvest_pct}%")

approved_date = deposit.approved_at.date()
mining_earning = Decimal(deposit.package.daily_earning)
print(f"Daily mining earning: Rs{mining_earning}")

start_balance = Decimal('700')
current_balance = start_balance
print(f"\nStarting balance: Rs{current_balance}")

for day_offset in range(1, 4):
    earned_date = approved_date + timedelta(days=day_offset)
    
    existing = DailyEarning.objects.filter(
        user=user,
        earned_date=earned_date,
        deposit=deposit
    ).exists()
    
    if existing:
        print(f"\nDay {day_offset} ({earned_date}): Already has earnings")
        continue
    
    print(f"\n--- Day {day_offset} ({earned_date}) ---")
    print(f"  Starting balance: Rs{current_balance}")
    
    roi_earning = (current_balance * roi_percentage) / 100
    print(f"  Mining: Rs{mining_earning}")
    print(f"  ROI ({roi_percentage}%): Rs{roi_earning}")
    
    total_daily = mining_earning + roi_earning
    reinvest_amount = (total_daily * reinvest_pct) / 100
    available_amount = total_daily - reinvest_amount
    
    print(f"  Total daily: Rs{total_daily}")
    print(f"  Reinvest ({reinvest_pct}%): Rs{reinvest_amount}")
    print(f"  Available: Rs{available_amount}")
    
    DailyEarning.objects.create(
        user=user,
        earning_type='mining',
        amount=mining_earning,
        deposit=deposit,
        earned_date=earned_date
    )
    
    DailyEarning.objects.create(
        user=user,
        earning_type='roi',
        amount=roi_earning,
        deposit=deposit,
        earned_date=earned_date
    )
    
    DailyEarning.objects.create(
        user=user,
        earning_type='reinvest',
        amount=reinvest_amount,
        deposit=deposit,
        earned_date=earned_date
    )
    
    Transaction.objects.create(
        user=user,
        transaction_type='mining',
        amount=mining_earning,
        description=f'Daily mining from {deposit.package.name}'
    )
    
    Transaction.objects.create(
        user=user,
        transaction_type='roi',
        amount=roi_earning,
        description=f'Daily ROI earning ({roi_percentage}%)'
    )
    
    Transaction.objects.create(
        user=user,
        transaction_type='reinvest',
        amount=reinvest_amount,
        description=f'Auto reinvest ({reinvest_pct}%)'
    )
    
    current_balance += total_daily
    print(f"  Ending balance: Rs{current_balance}")

print(f"\n" + "=" * 70)
print(f"FINAL BALANCE AFTER BACKFILL: Rs{current_balance}")
print("=" * 70)

wallet.mining_income += Decimal('10')
wallet.roi_earnings += (Decimal('7') + Decimal('7.07') + Decimal('7.14'))
wallet.balance = current_balance
wallet.last_earning_date = approved_date + timedelta(days=3)
wallet.save()

print(f"\nWallet updated:")
print(f"  Mining income: Rs{wallet.mining_income}")
print(f"  ROI earnings:  Rs{wallet.roi_earnings}")
print(f"  Balance:       Rs{wallet.balance}")
