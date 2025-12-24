import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== Storage Configuration ===')
print(f'USE_SUPABASE: {settings.USE_SUPABASE}')
print(f'USE_S3: {settings.USE_S3}')
print(f'SUPABASE_URL: {settings.SUPABASE_URL}')
print(f'SUPABASE_BUCKET: {settings.SUPABASE_BUCKET}')
print(f'MEDIA_URL: {settings.MEDIA_URL}')
print(f'Default Storage Backend: {settings.STORAGES["default"]["BACKEND"]}')

if settings.USE_SUPABASE:
    print('\n=== Testing Supabase Connection ===')
    try:
        from config.supabase_storage import SupabaseStorage
        storage = SupabaseStorage()
        print('OK: Supabase Storage initialized successfully')
        print(f'  Bucket: {storage.bucket_name}')
    except Exception as e:
        print(f'ERROR: Supabase Storage error: {str(e)}')
else:
    print('\nWARNING: Supabase is not enabled in settings')
