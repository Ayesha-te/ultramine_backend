from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_fix_deposit_proof_not_null_constraint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposit',
            name='deposit_proof',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.URLField(max_length=500),
        ),
        migrations.AlterField(
            model_name='order',
            name='txid_proof',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
