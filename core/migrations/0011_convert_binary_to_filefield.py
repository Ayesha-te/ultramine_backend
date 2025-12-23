from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_order_transaction_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deposit',
            name='deposit_proof_content_type',
        ),
        migrations.RemoveField(
            model_name='deposit',
            name='deposit_proof_filename',
        ),
        migrations.RemoveField(
            model_name='order',
            name='txid_proof_content_type',
        ),
        migrations.RemoveField(
            model_name='order',
            name='txid_proof_filename',
        ),
        migrations.RemoveField(
            model_name='product',
            name='image_content_type',
        ),
        migrations.RemoveField(
            model_name='product',
            name='image_filename',
        ),
        migrations.RemoveField(
            model_name='productimage',
            name='image_content_type',
        ),
        migrations.RemoveField(
            model_name='productimage',
            name='image_filename',
        ),
        migrations.AlterField(
            model_name='deposit',
            name='deposit_proof',
            field=models.FileField(blank=True, null=True, upload_to='deposit_proofs/'),
        ),
        migrations.AlterField(
            model_name='order',
            name='txid_proof',
            field=models.FileField(blank=True, null=True, upload_to='order_proofs/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='products/'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.FileField(upload_to='product_images/'),
        ),
    ]
