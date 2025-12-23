# 🎯 QUICK REFERENCE CARD

## Problem
Images disappear on Koyeb after restart ❌

## Solution
Use AWS S3 for persistent storage ✅

## Time Required
45 minutes total

---

## 📋 Files You Need

### Read These (Pick One)
- **Quick** → `KOYEB_QUICK_FIX.md` (5 min)
- **Detailed** → `KOYEB_SETUP_CHECKLIST.md` (30 min)
- **Overview** → `START_HERE.md` (5 min)

### Reference These
- AWS setup → `KOYEB_S3_SETUP.md`
- Code guide → `IMAGE_URL_GENERATION.md`
- Diagrams → `IMAGE_UPLOAD_FLOW.md`
- Env vars → `.env.koyeb.example`

---

## 🚀 5-Step Setup

### 1. AWS S3 Bucket (5 min)
```
Name: ultamine-media
Region: us-east-1
Public access: Enable
CORS: Enable
```

### 2. AWS IAM User (5 min)
```
Name: ultamine-s3-user
Policy: AmazonS3FullAccess
Generate: Access keys
Save: Keys securely!
```

### 3. Koyeb Environment (5 min)
```
USE_S3=True
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=ultamine-media
AWS_S3_REGION_NAME=us-east-1
```

### 4. Redeploy (5 min)
```
Push code or manual redeploy
Wait for deployment to complete
```

### 5. Test (5 min)
```
Upload image → Check S3 bucket
Verify display → Restart app
Image still there? ✅ Success!
```

---

## 🔧 Code Changes Made

### `config/settings.py`
```python
if USE_S3:
    STORAGES = {
        'default': S3Boto3Storage,
        'staticfiles': S3StaticStorage
    }
    MEDIA_URL = 'https://bucket.s3.amazonaws.com/media/'
else:
    MEDIA_URL = '/media/'
```

### `config/urls.py`
```python
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, ...)
    urlpatterns += static(settings.MEDIA_URL, ...)
```

---

## ✅ Success Indicators

- [x] Image uploads without error
- [x] File in S3 bucket
- [x] Image displays in app
- [x] Image URL starts with `https://s3.amazonaws.com`
- [x] No 404 or 403 errors
- [x] Image survives app restart

---

## 🆘 Common Issues

| Error | Fix |
|-------|-----|
| 403 Forbidden | Uncheck "Block public access" |
| 404 Not Found | Verify bucket name |
| CORS error | Configure CORS in S3 |
| Upload fails | Check AWS credentials |

---

## 📞 Documentation Map

```
START_HERE.md
    ↓
Choose your path:
    ├─ Quick → KOYEB_QUICK_FIX.md
    ├─ Detailed → KOYEB_SETUP_CHECKLIST.md
    ├─ Technical → IMAGE_UPLOAD_FLOW.md
    └─ Code → IMAGE_URL_GENERATION.md
```

---

## 💡 Key Points

✅ Code already updated  
✅ No database migrations  
✅ Works with local dev  
✅ Secure (env variables)  
✅ Cost effective  
✅ Production ready  

---

## 🎉 Result

Images will:
- Persist after restart ✅
- Persist after redeploy ✅
- Work everywhere ✅
- Be backed up ✅
- Scale globally ✅

---

**→ START WITH: `START_HERE.md`**
