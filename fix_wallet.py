import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Wallet, DailyEarning
from django.contrib.auth import get_user_model
from django.db.models import Sum
from decimal import Decimal

User = get_user_model()
user = User.objects.get(email='farah@gmail.com')
wallet = user.wallet

print("=" * 70)
print("WALLET AUDIT AND CORRECTION")
print("=" * 70)

print("\nCURRENT STATE:")
print(f"  Mining income:     Rs{wallet.mining_income}")
print(f"  ROI earnings:      Rs{wallet.roi_earnings}")
print(f"  Referral earnings: Rs{wallet.referral_earnings}")
print(f"  Balance:           Rs{wallet.balance}")

earnings_sum = DailyEarning.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
print(f"\n  Total daily earnings: Rs{earnings_sum}")

deposit_and_bonus = Decimal('700')  
print(f"  Deposits + bonuses:   Rs{deposit_and_bonus}")

expected_balance = deposit_and_bonus + earnings_sum
print(f"\nEXPECTED BALANCE: Rs{expected_balance}")
print(f"CURRENT BALANCE:  Rs{wallet.balance}")
print(f"DIFFERENCE:       Rs{wallet.balance - expected_balance}")

if wallet.balance != expected_balance:
    print(f"\nCORRECTING BALANCE...")
    wallet.balance = expected_balance
    wallet.save()
    print(f"NEW BALANCE: Rs{wallet.balance}")
    print("CORRECTED!")
else:
    print("\nBalance is correct!")
