import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import DailyEarning, Wallet
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()
user = User.objects.get(email='farah@gmail.com')
wallet = user.wallet

day3_balance = Decimal('724.12')
day3_earnings = Decimal('12.00')
final_balance = day3_balance + day3_earnings

print(f"Day 1-2 balance: Rs{day3_balance}")
print(f"Day 3 earnings: Rs{day3_earnings}")
print(f"Final balance:  Rs{final_balance}")

wallet.balance = final_balance
wallet.save()

print(f"\nWallet updated: Rs{wallet.balance}")
print(f"Mining income: Rs{wallet.mining_income}")
print(f"ROI earnings:  Rs{wallet.roi_earnings}")
