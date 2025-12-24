from django.db import migrations
import os


def convert_image_file_paths_to_urls(apps, schema_editor):
    """
    Convert file paths to proper Supabase URLs for Order.txid_proof, Product.image, and ProductImage.image.
    """
    Order = apps.get_model('core', 'Order')
    Product = apps.get_model('core', 'Product')
    ProductImage = apps.get_model('core', 'ProductImage')
    
    supabase_url = os.environ.get('SUPABASE_URL')
    bucket = os.environ.get('SUPABASE_BUCKET', 'ultramine')
    
    if not supabase_url:
        supabase_url = 'https://zgnllwrtqdiiunniwzkz.supabase.co'
    
    updated_count = 0
    cleared_count = 0
    
    # Fix Order.txid_proof
    for order in Order.objects.all():
        if not order.txid_proof:
            continue
        
        proof = order.txid_proof
        
        if isinstance(proof, str):
            if proof.startswith('http://') or proof.startswith('https://'):
                continue
            
            if proof.startswith('order_proofs/'):
                full_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{proof}"
                order.txid_proof = full_url
                order.save()
                updated_count += 1
            else:
                order.txid_proof = None
                order.save()
                cleared_count += 1
        else:
            order.txid_proof = None
            order.save()
            cleared_count += 1
    
    # Fix Product.image
    for product in Product.objects.all():
        if not product.image:
            continue
        
        image = product.image
        
        if isinstance(image, str):
            if image.startswith('http://') or image.startswith('https://'):
                continue
            
            if image.startswith('products/'):
                full_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{image}"
                product.image = full_url
                product.save()
                updated_count += 1
            else:
                product.image = None
                product.save()
                cleared_count += 1
        else:
            product.image = None
            product.save()
            cleared_count += 1
    
    # Fix ProductImage.image
    for product_image in ProductImage.objects.all():
        if not product_image.image:
            continue
        
        image = product_image.image
        
        if isinstance(image, str):
            if image.startswith('http://') or image.startswith('https://'):
                continue
            
            if image.startswith('product_images/'):
                full_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{image}"
                product_image.image = full_url
                product_image.save()
                updated_count += 1
            else:
                product_image.delete()
                cleared_count += 1
        else:
            product_image.delete()
            cleared_count += 1
    
    print(f"\nOrder/Product image migration complete:")
    print(f"  - Updated file paths to URLs: {updated_count}")
    print(f"  - Cleared invalid data: {cleared_count}")


def reverse_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_fix_deposit_proof_urls'),
    ]

    operations = [
        migrations.RunPython(convert_image_file_paths_to_urls, reverse_migration),
    ]
