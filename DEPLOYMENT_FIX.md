# Backend Deployment Fix

## Issue
The backend deployment was failing with the error:
```
ModuleNotFoundError: No module named 'core.wsgi'
```

The deployment platform was trying to load `core.wsgi:application`, but the actual WSGI module is located at `config.wsgi:application`.

## Solution

### 1. Procfile Configuration ✅
A `Procfile` has been created that specifies the correct WSGI module:
```
web: gunicorn config.wsgi:application
```

This tells the deployment platform (Koyeb/Heroku) to use the correct WSGI entry point.

### 2. Environment Variables Required

For the application to work in production, set the following environment variables on your deployment platform (Koyeb Dashboard):

#### Required
- **DJANGO_SETTINGS_MODULE**: `config.settings` (usually set automatically)
- **SECRET_KEY**: A secure Django secret key (change this in production!)
- **DEBUG**: `False` (important for production)
- **ALLOWED_HOSTS**: Your domain names (e.g., `yourdomain.com,www.yourdomain.com`)

#### Database Configuration
- **DATABASE_ENGINE**: `django.db.backends.postgresql`
- **DATABASE_NAME**: Your database name
- **DATABASE_USER**: Your database user
- **DATABASE_PASSWORD**: Your database password
- **DATABASE_HOST**: Your database host (e.g., Neon PostgreSQL URL)
- **DATABASE_PORT**: `5432` (default PostgreSQL port)

#### Site Configuration
- **SITE_URL**: Your deployed site URL (e.g., `https://grand-enrichetta-sagiyqwgey-54c3b5af.koyeb.app`)
  - **Important**: This is needed for image URLs to work correctly in API responses (proofs, products)
  - Use your full domain name with protocol (https:// for production)

#### AWS S3 (Optional but Recommended)
If you want to use S3 for file storage (recommended for production):
- **USE_S3**: `True`
- **AWS_ACCESS_KEY_ID**: Your AWS access key
- **AWS_SECRET_ACCESS_KEY**: Your AWS secret key
- **AWS_STORAGE_BUCKET_NAME**: Your S3 bucket name
- **AWS_S3_REGION_NAME**: `us-east-1` (or your region)

**S3 Setup Benefits:**
- More reliable file serving in production
- Better performance with CDN
- No need to manage local file storage

### 3. Running Database Migrations

After deploying with the Procfile, run migrations on the platform:

**On Koyeb:**
```bash
# Use the Koyeb CLI or dashboard to run a one-off command
koyeb exec config.wsgi -- python manage.py migrate
```

**Alternative (if you have SSH access):**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4. Creating a Superuser

After migrations, create a superuser account:
```bash
python manage.py createsuperuser
```

Or use the provided script:
```bash
python manage.py shell < create_superuser.py
```

### 5. Deployment Steps

1. **Push to your Git repository:**
   ```bash
   git add ultraminebackend/
   git commit -m "Fix: Add Procfile with correct WSGI configuration"
   git push origin main
   ```

2. **Redeploy on your platform:**
   - If using Koyeb: The deployment should automatically trigger and use the new Procfile
   - If using Heroku: Push to Heroku git remote
   - Ensure the platform detects it as a Python application

3. **Verify deployment:**
   - Check the deployment logs for "Worker booting" without errors
   - Visit your API endpoint to confirm it's working
   - Check the admin panel at `/admin`

## Key Points

- The `Procfile` tells the deployment platform how to start the application
- Django settings are configured in `config/settings.py`
- WSGI application is at `config/wsgi.py`
- Environment variables must be set on the deployment platform (not in .env)
- The `.env` file is for local development only

## Image Loading Issues (Proofs & Products)

### Problem
Images (deposit proofs, product images, transaction proofs) are not loading in production on Koyeb.

### Root Causes
1. **SITE_URL not configured**: Serializers don't know what domain to use for image URLs
2. **Media files not served**: `/media/` files are stored locally but not accessible in production
3. **Frontend requesting wrong URLs**: Image URLs default to `localhost:8000`

### Solution

#### Step 1: Set SITE_URL Environment Variable (Quick Fix)
On Koyeb Dashboard:
1. Go to your app settings
2. Set environment variable: `SITE_URL=https://your-app-domain.koyeb.app`
3. Redeploy the app

This ensures image URLs in API responses point to the correct domain.

#### Step 2: Use AWS S3 for Reliable File Storage (Recommended)

For production, use S3 instead of local storage:

**On Koyeb Dashboard, set these environment variables:**
```
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

**Benefits:**
- Images are reliably served from AWS CDN
- No local storage issues
- Better performance and scalability

#### Step 3: Verify Image URLs

After deployment, check that API responses return full URLs:
```bash
# Check deposit proofs
curl https://your-app-domain.koyeb.app/api/core/deposits/

# Check product images  
curl https://your-app-domain.koyeb.app/api/core/products/
```

Image URLs should look like:
- With SITE_URL fix: `https://your-app-domain.koyeb.app/media/products/image.png`
- With S3: `https://your-bucket.s3.amazonaws.com/media/products/image.png`

### Troubleshooting

**Images still showing as "localhost:8000" URLs:**
1. Verify SITE_URL is set correctly on Koyeb (with https://)
2. Redeploy/rebuild the app after changing env vars
3. Clear browser cache and reload

**Images returning 404 errors:**
1. Check if S3 bucket is accessible and credentials are correct
2. Verify `AWS_STORAGE_BUCKET_NAME` is set correctly
3. Check S3 bucket CORS settings if accessing from frontend

## Troubleshooting

If you still get `ModuleNotFoundError: No module named 'core.wsgi'`:

1. **Verify Procfile exists** in the root of `ultraminebackend/`
2. **Check platform settings**: Ensure the platform isn't overriding the Procfile with a custom build command
3. **Clear platform cache**: Rebuild/redeploy from scratch
4. **Check logs**: Look for the exact gunicorn command being run

## Files Modified

- Created: `Procfile` - Specifies the correct WSGI entry point
- Updated: `.env` - Added database configuration template
