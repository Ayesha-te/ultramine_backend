# Quick Koyeb Image Upload Fix - Step by Step

## Why Images Disappear on Koyeb?
Koyeb has an **ephemeral file system** - all uploaded files are deleted when the app restarts or redeploys. Solution: Use AWS S3.

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Create AWS S3 Bucket
```
1. Go to https://console.aws.amazon.com/
2. Search for "S3" → Create bucket
3. Name: ultamine-media (must be unique)
4. Region: us-east-1
5. Uncheck "Block public access"
```

### Step 2: Create IAM User
```
1. Go to IAM → Users → Create user
2. Name: ultamine-s3-user
3. Generate access key
4. Copy: Access Key ID and Secret Access Key
5. Attach policy: AmazonS3FullAccess
```

### Step 3: Configure S3 Bucket
```
Permissions → CORS → Add this:
{
  "AllowedHeaders": ["*"],
  "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
  "AllowedOrigins": ["*"],
  "ExposeHeaders": ["ETag"]
}
```

### Step 4: Add Koyeb Environment Variables
In your Koyeb project, add these:
```
USE_S3=True
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=ultamine-media
AWS_S3_REGION_NAME=us-east-1
```

### Step 5: Redeploy
```
Commit and push code → Koyeb redeploys → Done!
```

---

## ✅ Verify It Works

1. Upload an image in your app
2. Check AWS S3 console → your bucket → media folder
3. File should be there
4. Image should display in your app
5. URL should be: `https://ultamine-media.s3.amazonaws.com/media/...`

---

## 📋 Checklist Before Deploying

- [ ] S3 bucket created
- [ ] IAM user created with access key
- [ ] CORS configured on bucket
- [ ] Environment variables added to Koyeb
- [ ] `django-storages` in requirements.txt (already there ✓)
- [ ] App redeployed on Koyeb

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Images still not showing | Check Koyeb env vars, verify S3 bucket name |
| 403 Forbidden error | Check S3 public access settings, CORS config |
| Images upload but URL is broken | Verify AWS_STORAGE_BUCKET_NAME is correct |
| CORS errors in browser | Update S3 CORS configuration |

---

## 📚 More Information

- See `KOYEB_S3_SETUP.md` for detailed setup
- See `.env.koyeb.example` for all environment variables

---

**That's it! Your images will now persist on Koyeb.** 🎉
