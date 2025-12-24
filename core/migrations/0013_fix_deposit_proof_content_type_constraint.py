from django.db import migrations


def fix_not_null_constraint(apps, schema_editor):
    from django.db import connection
    
    cursor = connection.cursor()
    
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                ALTER TABLE core_deposit 
                DROP CONSTRAINT IF EXISTS core_deposit_deposit_proof_content_type_not_null;
            """)
        except Exception:
            pass
        
        try:
            cursor.execute("""
                ALTER TABLE core_deposit 
                ALTER COLUMN deposit_proof_content_type DROP NOT NULL;
            """)
        except Exception:
            pass
        
        try:
            cursor.execute("""
                DELETE FROM core_deposit 
                WHERE deposit_proof_content_type IS NULL 
                AND deposit_proof = '';
            """)
        except Exception:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_fix_deposit_proof_schema'),
    ]

    operations = [
        migrations.RunPython(fix_not_null_constraint, migrations.RunPython.noop),
    ]
