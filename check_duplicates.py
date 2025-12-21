import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import DailyEarning
from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()
user = User.objects.get(email='farah@gmail.com')

print("CHECKING FOR DUPLICATE EARNINGS RECORDS:")
print("=" * 60)

earnings_count = DailyEarning.objects.filter(user=user).values('earned_date', 'earning_type').annotate(count=Count('id')).order_by('earned_date')
for e in earnings_count:
    print(f"  {e['earned_date']} {e['earning_type']:12}: {e['count']} record(s)")

print("\nALL DAILY EARNINGS DETAILS:")
print("=" * 60)
all_earnings = DailyEarning.objects.filter(user=user).order_by('earned_date', 'earning_type', 'id')
total_mining = 0
total_roi = 0
total_reinvest = 0
for e in all_earnings:
    print(f"  ID:{e.id} {e.earned_date} {e.earning_type:12}: Rs{e.amount}")
    if e.earning_type == 'mining':
        total_mining += float(e.amount)
    elif e.earning_type == 'roi':
        total_roi += float(e.amount)
    elif e.earning_type == 'reinvest':
        total_reinvest += float(e.amount)

print("\nTOTALS:")
print(f"  Total Mining:   Rs{total_mining}")
print(f"  Total ROI:      Rs{total_roi}")
print(f"  Total Reinvest: Rs{total_reinvest}")
print(f"  Grand Total:    Rs{total_mining + total_roi + total_reinvest}")

print("\nWALLET INCOME FIELDS:")
wallet = user.wallet
print(f"  mining_income:     Rs{wallet.mining_income}")
print(f"  roi_earnings:      Rs{wallet.roi_earnings}")
print(f"  referral_earnings: Rs{wallet.referral_earnings}")
print(f"  balance:           Rs{wallet.balance}")
