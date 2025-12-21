import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import DailyEarning, Wallet, Transaction, Deposit, MiningPackage
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='farah@gmail.com')

print("=" * 60)
print("USER ACCOUNT:", user.email)
print("=" * 60)

print("\nPACKAGES:")
for pkg in MiningPackage.objects.all():
    print(f"  {pkg.name}: Rs{pkg.price} - Daily earning: Rs{pkg.daily_earning}")

print("\nYOUR DEPOSITS:")
for d in Deposit.objects.filter(user=user):
    print(f"  Rs{d.amount} ({d.package.name}) - Status: {d.status}")
    print(f"    Daily earning: Rs{d.package.daily_earning}")
    print(f"    Approved at: {d.approved_at}")

print("\nDAILY EARNINGS (from calculate_daily_earnings command):")
earnings = DailyEarning.objects.filter(user=user).order_by('earned_date')
if earnings.exists():
    for e in earnings:
        print(f"  {e.earned_date}: {e.earning_type.upper():12} -> Rs{e.amount}")
else:
    print("  EMPTY - No daily earnings generated!")

print("\nWALLET:")
wallet = user.wallet
print(f"  Mining income: Rs{wallet.mining_income}")
print(f"  ROI earnings:  Rs{wallet.roi_earnings}")
print(f"  Referral:      Rs{wallet.referral_earnings}")
print(f"  Balance:       Rs{wallet.balance}")
print(f"  Last earning:  {wallet.last_earning_date}")

print("\nTRANSACTIONS (recent):")
for t in Transaction.objects.filter(user=user).order_by('-created_at')[:10]:
    print(f"  {t.created_at.date()}: {t.transaction_type:12} -> Rs{t.amount:>10}")
