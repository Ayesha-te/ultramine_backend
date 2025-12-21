import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import DailyEarning, Wallet, Transaction, Deposit
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()
user = User.objects.get(email='farah@gmail.com')

print("=" * 70)
print("DETAILED BALANCE AUDIT")
print("=" * 70)

print("\n1. DEPOSIT INFO:")
deposits = Deposit.objects.filter(user=user)
for d in deposits:
    print(f"   Amount: Rs{d.amount}")
    print(f"   Approved: {d.approved_at}")
    print(f"   Days passed: {(datetime.now(d.approved_at.tzinfo) - d.approved_at).days} days")

print("\n2. ALL TRANSACTIONS (in chronological order):")
transactions = Transaction.objects.filter(user=user).order_by('created_at')
total_transactions = 0
for t in transactions:
    total_transactions += float(t.amount)
    print(f"   {t.created_at.date()}: {t.transaction_type:12} -> Rs{t.amount:>10} (total: Rs{total_transactions:>10})")

print(f"\n   CUMULATIVE FROM TRANSACTIONS: Rs{total_transactions}")

print("\n3. DAILY EARNINGS BREAKDOWN:")
daily_earnings = DailyEarning.objects.filter(user=user).order_by('earned_date')
print(f"   Total records: {daily_earnings.count()}")
for e in daily_earnings:
    print(f"   {e.earned_date}: {e.earning_type:12} -> Rs{e.amount:>10}")

from django.db.models import Sum
earnings_sum = daily_earnings.aggregate(Sum('amount'))['amount__sum'] or 0
print(f"   TOTAL DAILY EARNINGS: Rs{earnings_sum}")

print("\n4. WALLET STATE:")
wallet = user.wallet
print(f"   Mining income: Rs{wallet.mining_income}")
print(f"   ROI earnings:  Rs{wallet.roi_earnings}")
print(f"   Referral:      Rs{wallet.referral_earnings}")
print(f"   Balance:       Rs{wallet.balance}")

print("\n5. EXPECTED vs ACTUAL:")
print(f"   Deposits + bonuses: Rs{500 + 100 + 100} = Rs700")
print(f"   Daily earnings: Rs{earnings_sum}")
print(f"   Expected balance: Rs{700 + earnings_sum}")
print(f"   Actual balance:   Rs{wallet.balance}")
print(f"   DIFFERENCE: Rs{wallet.balance - (700 + earnings_sum)}")

print("\n6. CALCULATION CHECK:")
print(f"   500 (deposit) + 100 (signup) + 100 (other) + {earnings_sum} (earnings)")
print(f"   = Rs{500 + 100 + 100 + earnings_sum}")
