import os
import re

suspicious_patterns = []
for root, dirs, files in os.walk('core'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if 'wallet.balance +=' in line:
                        # Check if it's a legitimate earnings addition
                        if not any(x in line for x in ['mining_earning', 'roi_earning', 'referral_earning', 'signup_bonus', 'available_earning', 'reinvest_amount', 'earning']):
                            suspicious_patterns.append(f"{filepath}:{i}: {line.strip()}")

if suspicious_patterns:
    print("SUSPICIOUS: Found wallet.balance additions that might be deposits:")
    for p in suspicious_patterns:
        print(f"  {p}")
else:
    print("[OK] All wallet.balance additions are for earnings only (mining, ROI, referral, bonus, available)")
