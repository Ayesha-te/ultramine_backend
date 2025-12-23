import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Product, ProductImage
from core.serializers import ProductSerializer

print('Products:', Product.objects.count())
print('Product Images:', ProductImage.objects.count())

products = Product.objects.all()[:3]
for p in products:
    print(f'\nProduct {p.id}: {p.name}')
    print(f'  - has_image: {bool(p.image)}')
    print(f'  - image_filename: {p.image_filename}')
    print(f'  - product_images: {p.product_images.count()}')
    
    # Test serialization
    serializer = ProductSerializer(p)
    data = serializer.data
    print(f'  - image_url (from serializer): {type(data.get("image_url"))} - {str(data.get("image_url"))[:50] if data.get("image_url") else "None"}...')
    print(f'  - product_images (serialized): {len(data.get("product_images", []))}')
