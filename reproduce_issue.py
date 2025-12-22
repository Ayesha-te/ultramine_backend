import os
import django
from decimal import Decimal
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Deposit
from core.serializers import DepositSerializer

def run():
    print("Starting reproduction script...")
    
    # Ensure we have some data
    try:
        deposits = Deposit.objects.all()
        print(f"Found {deposits.count()} deposits.")
        
        for deposit in deposits:
            print(f"Processing deposit {deposit.id}...")
            try:
                print(f"  User ID: {deposit.user_id}")
                try:
                    print(f"  User: {deposit.user}")
                except Exception as e:
                    print(f"  Error accessing user: {e}")

                print(f"  Package ID: {deposit.package_id}")
                try:
                    print(f"  Package: {deposit.package}")
                    print(f"  Package Name: {deposit.package.name}")
                except Exception as e:
                    print(f"  Error accessing package: {e}")

                print(f"  Deposit Proof: {deposit.deposit_proof}")
                print(f"  Status: {deposit.status}")
                print(f"  Approved At: {deposit.approved_at}")
                
                if deposit.deposit_proof:
                    try:
                        print(f"  Deposit Proof URL: {deposit.deposit_proof.url}")
                    except Exception as e:
                        print(f"  Error accessing deposit_proof.url: {e}")

                try:
                    print(f"  Remaining Days: {deposit.remaining_days}")
                except Exception as e:
                    print(f"  Error accessing remaining_days: {e}")

                serializer = DepositSerializer(deposit)
                data = serializer.data
                # print(f"Successfully serialized deposit {deposit.id}")
            except Exception as e:
                print(f"Error serializing deposit {deposit.id}: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"General error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run()
