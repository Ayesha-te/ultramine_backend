# Image URL Generation - How It Works

## Overview
This document explains how image URLs are generated and returned to the frontend, especially for Koyeb with S3 storage.

---

## Current Implementation in Serializers

### DepositSerializer - Image URL Generation
Located in: `core/serializers.py`

```python
def get_deposit_proof_url(self, obj):
    if obj.deposit_proof:
        # Get the URL from the image field
        url = obj.deposit_proof.url if hasattr(obj.deposit_proof, 'url') else str(obj.deposit_proof)
        
        # If URL doesn't start with http, it's relative - construct full URL
        if url and not url.startswith('http'):
            request = self.context.get('request')
            if request:
                # Use request context to build base URL
                base_url = f"{request.scheme}://{request.get_host()}".rstrip('/')
            else:
                # Fallback to settings
                base_url = getattr(settings, 'SITE_URL', '').rstrip('/')
                if not base_url:
                    base_url = 'http://localhost:8000'
            return f"{base_url}{url}"
        return url
    return None
```

---

## Image URL Flow

### Local Development (USE_S3=False)
```
1. User uploads image
2. Saved to: /media/deposit_proofs/image_abc123.jpg
3. Django model stores: deposit_proofs/image_abc123.jpg
4. Serializer gets: /media/deposit_proofs/image_abc123.jpg (relative)
5. Since URL doesn't start with 'http':
   - Build base_url: http://localhost:8000
   - Return: http://localhost:8000/media/deposit_proofs/image_abc123.jpg
6. Frontend fetches from Django (served locally)
```

### Production on Koyeb (USE_S3=True)
```
1. User uploads image
2. django-storages uploads to S3
3. Stored in S3 at: s3://ultamine-media/media/deposit_proofs/image_abc123.jpg
4. Django model stores: deposit_proofs/image_abc123.jpg
5. Serializer gets: https://ultamine-media.s3.amazonaws.com/media/deposit_proofs/image_abc123.jpg (full URL)
6. Since URL starts with 'https://' (http):
   - Return as-is: https://ultamine-media.s3.amazonaws.com/media/deposit_proofs/image_abc123.jpg
7. Frontend fetches directly from S3
```

---

## Image Fields in Models

### Fields Using Images:

#### 1. **Deposit Model** - `deposit_proof`
```python
deposit_proof = models.ImageField(upload_to='deposit_proofs/', null=True, blank=True)
```
- Used for: Proof of payment/deposit
- Stored at: `s3://bucket/media/deposit_proofs/`
- URL: `/deposit_proofs/filename.jpg` → `https://s3.amazonaws.com/.../deposit_proofs/...`

#### 2. **Product Model** - `image`
```python
image = models.ImageField(upload_to='products/', null=True, blank=True)
```
- Used for: Product photo
- Stored at: `s3://bucket/media/products/`
- URL: `/products/filename.jpg` → `https://s3.amazonaws.com/.../products/...`

#### 3. **ProductImage Model** - `image`
```python
image = models.ImageField(upload_to='products/')
```
- Used for: Additional product images
- Stored at: `s3://bucket/media/products/`
- URL: `/products/filename.jpg` → `https://s3.amazonaws.com/.../products/...`

#### 4. **Order Model** - `txid_proof`
```python
txid_proof = models.ImageField(upload_to='txid_proofs/', null=True, blank=True)
```
- Used for: Transaction ID proof
- Stored at: `s3://bucket/media/txid_proofs/`
- URL: `/txid_proofs/filename.jpg` → `https://s3.amazonaws.com/.../txid_proofs/...`

---

## Serializer Methods for Image URLs

All image URL methods follow the same pattern:

```python
def get_{field}_url(self, obj):
    if obj.{field}:
        url = obj.{field}.url if hasattr(obj.{field}, 'url') else str(obj.{field})
        if url and not url.startswith('http'):
            request = self.context.get('request')
            if request:
                base_url = f"{request.scheme}://{request.get_host()}".rstrip('/')
            else:
                base_url = getattr(settings, 'SITE_URL', '').rstrip('/')
                if not base_url:
                    base_url = 'http://localhost:8000'
            return f"{base_url}{url}"
        return url
    return None
```

---

## How django-storages Works

### Storage Backend Configuration:
```python
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        'OPTIONS': {
            'location': 'media',      # All files go to s3://bucket/media/
            'file_overwrite': False   # Don't overwrite existing files
        }
    }
}
```

### File Upload Process:
```
1. User uploads file
2. Django calls save() on ImageField
3. django-storages intercepts
4. Uploads to S3: s3://bucket/media/upload_to/filename
5. Returns: https://bucket.s3.amazonaws.com/media/upload_to/filename
6. Model stores: upload_to/filename (relative path)
```

### Image URL Resolution:
```
When you access obj.image.url:
- Local: Returns /media/upload_to/filename
- S3: Returns https://bucket.s3.amazonaws.com/media/upload_to/filename
```

---

## Environment-Specific Behavior

### Development (USE_S3=False)
```
settings.py:
  MEDIA_URL = '/media/'
  MEDIA_ROOT = BASE_DIR / 'media'

URL returned:
  /media/products/image.jpg

Full URL in response:
  http://localhost:8000/media/products/image.jpg (added by serializer)

Served by:
  Django development server
```

### Production on Koyeb (USE_S3=True)
```
settings.py:
  MEDIA_URL = 'https://ultamine-media.s3.amazonaws.com/media/'
  STORAGES['default'] = S3Boto3Storage

URL returned:
  https://ultamine-media.s3.amazonaws.com/media/products/image.jpg

Served by:
  AWS S3 (persists across restarts!)

Note:
  Serializer detects 'https://' prefix and returns as-is
```

---

## Example API Responses

### GET /api/core/deposits/123/

#### Local Development:
```json
{
  "id": 123,
  "amount": 1000,
  "status": "pending",
  "deposit_proof": "deposit_proofs/proof_abc123.jpg",
  "deposit_proof_url": "http://localhost:8000/media/deposit_proofs/proof_abc123.jpg",
  "created_at": "2024-12-23T10:00:00Z"
}
```

#### Koyeb with S3:
```json
{
  "id": 123,
  "amount": 1000,
  "status": "pending",
  "deposit_proof": "deposit_proofs/proof_abc123.jpg",
  "deposit_proof_url": "https://ultamine-media.s3.amazonaws.com/media/deposit_proofs/proof_abc123.jpg",
  "created_at": "2024-12-23T10:00:00Z"
}
```

---

## Frontend Usage

### React/Vue Example:
```javascript
// Fetch deposit data
const deposit = await fetch('/api/core/deposits/123/').then(r => r.json());

// Display image using the _url field
<img src={deposit.deposit_proof_url} alt="Proof" />

// In local dev: src="http://localhost:8000/media/..."
// In Koyeb:     src="https://ultamine-media.s3.amazonaws.com/media/..."
```

---

## Troubleshooting URL Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| 404 on image | Relative URL not being converted | Check request context in serializer |
| Image loads locally but not on Koyeb | Local path used instead of S3 | Set USE_S3=True, add AWS env vars |
| Incorrect domain in URL | Wrong SITE_URL setting | Check settings.SITE_URL for non-request context |
| CORS error on S3 image | S3 CORS not configured | Configure S3 bucket CORS |
| Mixed content error (https) | Loading http on https site | Ensure S3 URL uses https:// |

---

## Summary

The image URL system is designed to:
1. ✅ Work locally without S3 setup
2. ✅ Automatically use S3 when enabled
3. ✅ Return full URLs to frontend
4. ✅ Handle both relative and absolute paths
5. ✅ Support multiple deployment environments

When deployed to Koyeb with `USE_S3=True`, images automatically serve from S3 and persist across restarts! 🎉
