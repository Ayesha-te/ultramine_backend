# Koyeb S3 Setup - Complete Checklist

## 📋 Pre-Setup Requirements
- [ ] AWS account (free tier works)
- [ ] Access to your Koyeb dashboard
- [ ] Git access to your repository
- [ ] Understanding of environment variables

---

## 🚀 Phase 1: AWS Setup (15-20 minutes)

### Step 1.1: Create S3 Bucket
- [ ] Go to https://console.aws.amazon.com/
- [ ] Sign in to your AWS account
- [ ] Search for "S3" in services
- [ ] Click "Create bucket"
  - [ ] Name: `ultamine-media` (must be unique globally)
  - [ ] Region: `us-east-1` (or your preference)
  - [ ] Keep other defaults
- [ ] Click "Create bucket"

### Step 1.2: Configure Bucket Public Access
- [ ] Open the bucket you just created
- [ ] Go to "Permissions" tab
- [ ] Under "Block public access settings"
  - [ ] Uncheck "Block all public access"
  - [ ] Confirm the warning
- [ ] Click "Save changes"

### Step 1.3: Enable CORS
- [ ] Stay in "Permissions" tab
- [ ] Scroll to "Cross-origin resource sharing (CORS)"
- [ ] Click "Edit"
- [ ] Paste this JSON:
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
- [ ] Click "Save changes"

### Step 1.4: Create IAM User
- [ ] Go to IAM service (search in console)
- [ ] Click "Users" in left menu
- [ ] Click "Create user"
  - [ ] Name: `ultamine-s3-user`
  - [ ] Uncheck "Provide user access to AWS Management Console"
  - [ ] Click "Next"
- [ ] Click "Attach policies directly"
- [ ] Search for "AmazonS3FullAccess"
  - [ ] Check the checkbox
  - [ ] Click "Next"
- [ ] Click "Create user"

### Step 1.5: Generate Access Keys
- [ ] Click on the newly created user
- [ ] Go to "Security credentials" tab
- [ ] Under "Access keys", click "Create access key"
- [ ] Select "Application running outside AWS"
- [ ] Check "I understand the above recommendation"
- [ ] Click "Next"
- [ ] Click "Create access key"
- [ ] **IMPORTANT**: Click "Show" and copy:
  - [ ] Access Key ID (e.g., AKIA...)
  - [ ] Secret access key
- [ ] **Save these somewhere safe!** (You won't see them again)

---

## 🔧 Phase 2: Django Backend Setup (5 minutes)

### Step 2.1: Verify Django Configuration
- [ ] Open: `ultraminebackend/config/settings.py`
- [ ] Check that `django-storages` section exists
- [ ] Verify S3 configuration includes:
  - [ ] `STORAGES` with S3Boto3Storage
  - [ ] `MEDIA_URL` with S3 domain
  - [ ] Proper location paths

### Step 2.2: Verify Requirements
- [ ] Check `ultraminebackend/requirements.txt`
- [ ] Confirm it contains:
  - [ ] `django-storages==1.14.2` or newer
  - [ ] `boto3==1.28.45` or newer
- [ ] If missing, add them and commit

### Step 2.3: Create Environment File (Optional, for reference)
- [ ] Copy `.env.koyeb.example` to `.env.koyeb`
- [ ] Fill in your actual values:
  - [ ] AWS_ACCESS_KEY_ID=AKIA...
  - [ ] AWS_SECRET_ACCESS_KEY=your_secret
  - [ ] AWS_STORAGE_BUCKET_NAME=ultamine-media
  - [ ] AWS_S3_REGION_NAME=us-east-1
  - [ ] Other required variables

### Step 2.4: Commit Changes
- [ ] Run: `git add .`
- [ ] Run: `git commit -m "Configure S3 for Koyeb image uploads"`
- [ ] Run: `git push origin main` (or your branch)

---

## 🌐 Phase 3: Koyeb Configuration (10 minutes)

### Step 3.1: Access Koyeb Dashboard
- [ ] Go to https://app.koyeb.com/
- [ ] Log in to your account
- [ ] Select your application

### Step 3.2: Add Environment Variables
- [ ] Go to "Settings" or "Environment" section
- [ ] Add the following variables:
  ```
  USE_S3=True
  AWS_ACCESS_KEY_ID=AKIA...
  AWS_SECRET_ACCESS_KEY=your_secret_key
  AWS_STORAGE_BUCKET_NAME=ultamine-media
  AWS_S3_REGION_NAME=us-east-1
  ```
- [ ] Save the variables

### Step 3.3: Verify Other Important Variables
- [ ] Check that you have:
  - [ ] `DEBUG=False` (for production)
  - [ ] `ALLOWED_HOSTS` includes your domain
  - [ ] `DATABASE_URL` or database credentials
  - [ ] `SECRET_KEY` is set securely
  - [ ] `CORS_ALLOWED_ORIGINS` includes your frontend

### Step 3.4: Redeploy Application
- [ ] Trigger a new deployment:
  - [ ] Option 1: Go to "Deployments" → "Redeploy"
  - [ ] Option 2: Push new commit to trigger auto-deploy
- [ ] Wait for deployment to complete
- [ ] Check logs for errors

---

## ✅ Phase 4: Testing (5-10 minutes)

### Step 4.1: Test Image Upload
- [ ] Go to your app: `https://your-app.koyeb.app/`
- [ ] Find an image upload feature (e.g., deposit, product, order)
- [ ] Upload a test image
- [ ] Observe the response/check API

### Step 4.2: Verify S3 Storage
- [ ] Go to AWS S3 console
- [ ] Open your bucket: `ultamine-media`
- [ ] You should see a `media/` folder
- [ ] Navigate into it and find your uploaded image
- [ ] Confirm file exists: `media/[upload_path]/filename.jpg`

### Step 4.3: Verify Image Display
- [ ] In your app, check that the image displays
- [ ] Open browser DevTools → Network tab
- [ ] Check the image request:
  - [ ] Should be to: `https://ultamine-media.s3.amazonaws.com/media/...`
  - [ ] Should return: 200 OK with image data
  - [ ] Should NOT return: 403 Forbidden or 404 Not Found

### Step 4.4: Test App Restart
- [ ] Trigger a new deployment/restart
- [ ] Go back to the image in your app
- [ ] Image should still be visible ✅
- [ ] (It would have disappeared if stored locally)

---

## 🆘 Phase 5: Troubleshooting

### Issue: Image Upload Fails
- [ ] Check Koyeb logs for S3 errors
- [ ] Verify AWS credentials are correct
- [ ] Verify bucket name is correct
- [ ] Ensure IAM user has AmazonS3FullAccess

### Issue: 403 Forbidden on Image
- [ ] Check S3 bucket public access settings
- [ ] Verify CORS configuration
- [ ] Check bucket policy allows public read
- [ ] Ensure S3 URL has `https://`

### Issue: CORS Error in Browser
- [ ] Check browser console for specific error
- [ ] Verify S3 CORS configuration
- [ ] Consider adding your frontend domain to AllowedOrigins
- [ ] Clear browser cache

### Issue: Image URL is Incomplete
- [ ] Check `MEDIA_URL` in settings.py
- [ ] Verify it includes `https://` and bucket name
- [ ] Check AWS_STORAGE_BUCKET_NAME is correct
- [ ] Verify S3 region matches AWS_S3_REGION_NAME

### Issue: Koyeb Won't Deploy
- [ ] Check deployment logs
- [ ] Verify environment variables are set
- [ ] Ensure requirements.txt has all packages
- [ ] Check for syntax errors in settings.py
- [ ] Try manual redeploy

---

## 📊 Phase 6: Monitoring

### Regular Checks
- [ ] Weekly: Check S3 storage cost in AWS billing
- [ ] Monthly: Review unused files and delete
- [ ] Monthly: Check Koyeb logs for S3 errors
- [ ] Quarterly: Review CORS settings

### Cost Management
- [ ] Monitor S3 storage usage in CloudWatch
- [ ] Delete test images and old uploads
- [ ] Set up S3 Lifecycle policies for old files (optional)
- [ ] Consider enabling S3 Intelligent-Tiering

### Performance
- [ ] Monitor image load times
- [ ] Consider CloudFront CDN (optional)
- [ ] Review S3 request metrics
- [ ] Optimize image sizes on frontend

---

## 🎯 Success Criteria

### When everything is working:
- ✅ Images upload without errors
- ✅ Images appear in S3 bucket
- ✅ Images display in your app
- ✅ Images persist after app restart
- ✅ Images persist after redeployment
- ✅ Image URLs start with `https://ultamine-media.s3.amazonaws.com`
- ✅ No 404 or 403 errors in browser console
- ✅ No CORS errors in console

---

## 📚 Quick Reference

### AWS S3 Bucket Setup
```
Name: ultamine-media
Region: us-east-1
Public access: Disabled "Block all public access"
CORS: Enabled for all methods
```

### IAM User
```
Name: ultamine-s3-user
Policy: AmazonS3FullAccess
```

### Koyeb Environment Variables
```
USE_S3=True
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=ultamine-media
AWS_S3_REGION_NAME=us-east-1
```

### Django Settings (Already Configured ✅)
```
STORAGES = {
    'default': S3Boto3Storage,
    'staticfiles': S3StaticStorage
}
MEDIA_URL = https://ultamine-media.s3.amazonaws.com/media/
```

---

## ⏱️ Total Setup Time
- Phase 1 (AWS Setup): 15-20 minutes
- Phase 2 (Django): 5 minutes
- Phase 3 (Koyeb): 10 minutes
- Phase 4 (Testing): 5-10 minutes
- **Total: ~35-45 minutes**

---

## 🎉 You're Done!

Once all checkboxes are marked, your images will:
- ✅ Upload to S3 automatically
- ✅ Persist across restarts
- ✅ Persist across redeployments
- ✅ Be accessible globally
- ✅ Be backed up by AWS

Happy uploading! 📸
