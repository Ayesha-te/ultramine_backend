from django.db import migrations


def fix_not_null_constraint(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_fix_deposit_proof_schema'),
    ]

    operations = [
        migrations.RunPython(fix_not_null_constraint, migrations.RunPython.noop),
    ]
