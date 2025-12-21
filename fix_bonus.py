import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Transaction
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='farah@gmail.com')

print("FIXING BONUS SYSTEM:")
print("=" * 60)
print("\nTransactions before fix:")
deposits = Transaction.objects.filter(user=user, transaction_type='deposit').order_by('created_at')
for t in deposits:
    print(f"  {t.created_at.date()}: {t.description} -> Rs{t.amount}")

try:
    extra_bonus = Transaction.objects.get(
        user=user, 
        transaction_type='deposit',
        amount=100,
        created_at__date='2025-12-15'
    )
    print(f"\nRemoving extra bonus: {extra_bonus.description}")
    extra_bonus.delete()
except:
    print("\nNo extra bonus found to remove")

print("\nTransactions after fix:")
deposits = Transaction.objects.filter(user=user, transaction_type='deposit').order_by('created_at')
total = 0
for t in deposits:
    total += float(t.amount)
    print(f"  {t.created_at.date()}: {t.description} -> Rs{t.amount}")

print(f"\nTotal deposits + bonuses: Rs{total}")

correct_balance = 600 + 36.12
user.wallet.balance = correct_balance
user.wallet.save()
print(f"Wallet corrected to: Rs{correct_balance}")
