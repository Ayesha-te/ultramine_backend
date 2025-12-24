from django.db import migrations
import os
from django.conf import settings


def convert_file_paths_to_urls(apps, schema_editor):
    """
    Convert file paths to proper Supabase URLs and remove binary data.
    """
    Deposit = apps.get_model('core', 'Deposit')
    
    supabase_url = os.environ.get('SUPABASE_URL')
    bucket = os.environ.get('SUPABASE_BUCKET', 'ultramine')
    
    if not supabase_url:
        supabase_url = 'https://zgnllwrtqdiiunniwzkz.supabase.co'
    
    updated_count = 0
    cleared_count = 0
    
    for deposit in Deposit.objects.all():
        if not deposit.deposit_proof:
            continue
        
        proof = deposit.deposit_proof
        
        if isinstance(proof, str):
            if proof.startswith('http://') or proof.startswith('https://'):
                continue
            
            if proof.startswith('deposit_proofs/'):
                full_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{proof}"
                deposit.deposit_proof = full_url
                deposit.save()
                updated_count += 1
            else:
                deposit.deposit_proof = None
                deposit.save()
                cleared_count += 1
        else:
            deposit.deposit_proof = None
            deposit.save()
            cleared_count += 1
    
    print(f"\nDeposit proof migration complete:")
    print(f"  - Updated file paths to URLs: {updated_count}")
    print(f"  - Cleared invalid data: {cleared_count}")


def reverse_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_convert_filefield_to_urlfield'),
    ]

    operations = [
        migrations.RunPython(convert_file_paths_to_urls, reverse_migration),
    ]
