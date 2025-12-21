import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Wallet
from django.db.models import Sum

def fix_wallet_balances():
    """Recalculate wallet balances to exclude deposits (only earnings)"""
    wallets = Wallet.objects.all()
    updated_count = 0
    
    for wallet in wallets:
        correct_balance = (
            wallet.mining_income + 
            wallet.roi_earnings + 
            wallet.referral_earnings + 
            wallet.signup_bonus
        )
        
        if wallet.balance != correct_balance:
            old_balance = wallet.balance
            wallet.balance = correct_balance
            wallet.save()
            updated_count += 1
            print(f"[FIXED] {wallet.user.email}: {old_balance} -> {correct_balance} PKR")
        else:
            print(f"[OK] {wallet.user.email}: Already correct ({correct_balance} PKR)")
    
    print(f"\n[SUCCESS] Fixed {updated_count} wallets")

if __name__ == "__main__":
    print("Fixing wallet balances (removing deposits, keeping only earnings)...\n")
    fix_wallet_balances()
    print("\nDone!")
