from django.db import migrations


def drop_columns_if_exist(apps, schema_editor):
    from django.db import connection
    cursor = connection.cursor()
    
    tables_columns = [
        ('core_deposit', 'deposit_proof_content_type'),
        ('core_deposit', 'deposit_proof_filename'),
        ('core_order', 'txid_proof_content_type'),
        ('core_order', 'txid_proof_filename'),
        ('core_product', 'image_content_type'),
        ('core_product', 'image_filename'),
        ('core_productimage', 'image_content_type'),
        ('core_productimage', 'image_filename'),
    ]
    
    for table, column in tables_columns:
        try:
            cursor.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS {column};")
        except Exception as e:
            print(f"Error dropping {column} from {table}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_convert_binary_to_filefield'),
    ]

    operations = [
        migrations.RunPython(drop_columns_if_exist, migrations.RunPython.noop),
    ]
