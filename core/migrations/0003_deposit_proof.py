# Generated migration for adding deposit_proof field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deposit',
            name='deposit_proof',
            field=models.ImageField(blank=True, null=True, upload_to='deposit_proofs/'),
        ),
    ]
