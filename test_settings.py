#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

try:
    django.setup()
    print("✓ Settings loaded successfully")
    from django.conf import settings
    print(f"✓ USE_S3: {getattr(settings, 'USE_S3', 'Not defined')}")
    print(f"✓ MEDIA_URL: {settings.MEDIA_URL}")
    print(f"✓ MEDIA_ROOT: {settings.MEDIA_ROOT}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
