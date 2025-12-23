# Koyeb Deployment - Image Upload Fix Guide

## Problem
Koyeb uses an **ephemeral filesystem**, which means:
- Files uploaded to local disk are deleted when the app restarts or deploys
- Images are not visible after deployment
- The `/media/` directory is not persistent

## Solution: Use AWS S3 for Media Storage

### Step 1: Set Up AWS S3 Bucket

1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to S3 and create a new bucket
3. Name it something like: `ultamine-media` (must be globally unique)
4. Choose region: `us-east-1` (or your preferred region)
5. **IMPORTANT**: Uncheck "Block all public access" (or configure bucket policy)

### Step 2: Create IAM User with S3 Access

1. Go to IAM → Users → Create User
2. Name it: `ultamine-s3-user`
3. Click "Create access key"
4. Copy the **Access Key ID** and **Secret Access Key**
5. Attach policy: `AmazonS3FullAccess` (or create custom policy for specific bucket)

### Step 3: Configure S3 Bucket Policy (Optional but Recommended)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::ultamine-media/*"
    }
  ]
}
```

### Step 4: Enable CORS on S3 Bucket

Go to S3 → Your Bucket → Permissions → CORS:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

### Step 5: Add Environment Variables to Koyeb

Deploy your app on Koyeb and add these environment variables:

```
USE_S3=True
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_STORAGE_BUCKET_NAME=ultamine-media
AWS_S3_REGION_NAME=us-east-1
```

### Step 6: Install Required Package

Make sure `django-storages` is in your `requirements.txt`:

```
django-storages[s3]
boto3
botocore
```

If not, add it and redeploy:

```bash
pip install django-storages boto3
```

### Step 7: Collect Static Files (Production)

Before deploying, run locally:

```bash
python manage.py collectstatic --noinput
```

This will upload static files to S3.

## Django Settings (Already Configured)

The following settings are already configured in `config/settings.py`:

```python
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    # Storage backend configuration
    STORAGES = {
        'default': {  # For media files (user uploads)
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {
                'location': 'media',
                'file_overwrite': False,
            }
        },
        'staticfiles': {  # For static files (CSS, JS)
            'BACKEND': 'storages.backends.s3boto3.S3StaticStorage',
            'OPTIONS': {
                'location': 'static',
            }
        }
    }
    
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
    STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
```

## How It Works After Setup

1. **User uploads image from frontend**
2. Django receives the file
3. `django-storages` automatically uploads to S3
4. Database stores: `media/products/image.jpg` (relative path)
5. Serializer returns full S3 URL: `https://ultamine-media.s3.amazonaws.com/media/products/image.jpg`
6. Frontend displays image from S3

## Deployment Checklist

- [ ] AWS S3 bucket created
- [ ] IAM user with S3 access created
- [ ] S3 bucket CORS configured
- [ ] `django-storages[s3]` in requirements.txt
- [ ] Environment variables added to Koyeb
- [ ] `collectstatic` run locally or in Koyeb build script
- [ ] App redeployed on Koyeb

## Testing

After deployment:

1. Go to your Koyeb app
2. Upload an image
3. Check S3 bucket - file should be there
4. Image URL should be: `https://your-bucket.s3.amazonaws.com/media/...`
5. Image should load on frontend

## Troubleshooting

### Images still not showing?
- Check Koyeb environment variables
- Verify S3 bucket name is correct
- Check AWS credentials are valid
- Look at CloudWatch logs for errors

### Permission denied error?
- Verify IAM user has S3 full access
- Check bucket policy allows the IAM user
- Verify AWS credentials in Koyeb env vars

### 403 Forbidden on S3 URL?
- Check bucket public access settings
- Verify CORS configuration
- Check bucket policy allows public read

### CORS errors in browser console?
- Review S3 CORS configuration
- Add your frontend domain to AllowedOrigins
- Or use `"AllowedOrigins": ["*"]` for development

## Cost Considerations

- S3 storage: ~$0.023 per GB/month
- Data transfer: ~$0.09 per GB (varies by region)
- API calls: included in pricing
- **Tip**: Delete old unused images to reduce storage costs

## Alternative: Use CloudFront CDN (Optional)

For better performance, use CloudFront in front of S3:

1. Create CloudFront distribution pointing to your S3 bucket
2. Update `AWS_S3_CUSTOM_DOMAIN` to your CloudFront domain
3. This caches images globally for faster delivery

## Reference Documentation

- [Django Storages Documentation](https://django-storages.readthedocs.io/en/latest/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Koyeb Documentation](https://koye.readme.io/)
