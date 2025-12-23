# 🎯 KOYEB IMAGE UPLOAD FIX - MASTER GUIDE

## ⚡ TL;DR (Too Long; Didn't Read)

**Problem:** Images disappear on Koyeb after restart  
**Cause:** Koyeb has ephemeral file system (files deleted on restart)  
**Solution:** Use AWS S3 instead of local storage  
**Time:** 45 minutes to fix  
**Cost:** $0.023/GB/month for S3

---

## 📋 What You Need

### ✅ Already Done (Code)
- [x] Django settings configured for S3
- [x] URLs configured for static files
- [x] django-storages in requirements.txt
- [x] Comprehensive documentation created

### ⏳ You Need To Do (AWS + Koyeb)
- [ ] Create AWS S3 bucket
- [ ] Create AWS IAM user
- [ ] Add environment variables to Koyeb
- [ ] Redeploy your app
- [ ] Test image upload

---

## 🚀 Quick 5-Step Setup

### Step 1: Create S3 Bucket (3 min)
```
AWS Console → S3 → Create bucket
- Name: ultamine-media
- Region: us-east-1
- Uncheck "Block public access"
```

### Step 2: Configure Bucket (2 min)
```
- Enable CORS (copy config from docs)
```

### Step 3: Create IAM User (5 min)
```
AWS Console → IAM → Create user
- Name: ultamine-s3-user
- Attach: AmazonS3FullAccess
- Create access keys
- Copy and save the keys!
```

### Step 4: Add Koyeb Environment Variables (5 min)
```
USE_S3=True
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=ultamine-media
AWS_S3_REGION_NAME=us-east-1
```

### Step 5: Redeploy (5 min)
```
Push code or manually redeploy in Koyeb
```

**Total Time: ~20-30 minutes** ⏱️

---

## 📚 Documentation Reference

| Need | Document | Time |
|------|----------|------|
| Just tell me what to do | [KOYEB_QUICK_FIX.md](KOYEB_QUICK_FIX.md) | 5 min |
| Step-by-step with checkboxes | [KOYEB_SETUP_CHECKLIST.md](KOYEB_SETUP_CHECKLIST.md) | 30 min |
| Detailed AWS setup | [KOYEB_S3_SETUP.md](KOYEB_S3_SETUP.md) | 20 min |
| How the code works | [IMAGE_URL_GENERATION.md](IMAGE_URL_GENERATION.md) | 15 min |
| See architecture diagrams | [IMAGE_UPLOAD_FLOW.md](IMAGE_UPLOAD_FLOW.md) | 15 min |
| What was implemented | [KOYEB_IMPLEMENTATION_SUMMARY.md](KOYEB_IMPLEMENTATION_SUMMARY.md) | 10 min |
| Environment variables | [.env.koyeb.example](.env.koyeb.example) | 5 min |
| Full index | [README_KOYEB_IMAGE_FIX.md](README_KOYEB_IMAGE_FIX.md) | 5 min |

---

## 🎯 Before & After

### BEFORE (Broken ❌)
```
Frontend          Backend (Koyeb)          Storage
  │                    │                        │
  │──upload image──→   │                        │
  │                    │──save to /media/──→    │
  │                    │     (ephemeral)        │
  │                 [Restart]                   │
  │                    │                        │
  │  [Request image]   │                        │
  │   ← ❌ 404 Error    │  File deleted! ×      │
  │
  Images disappear when Koyeb restarts
```

### AFTER (Fixed ✅)
```
Frontend          Backend (Koyeb)          AWS S3 (Permanent)
  │                    │                        │
  │──upload image──→   │                        │
  │                    │──upload to S3──────→   │
  │                    │ (via boto3)             │
  │                                     (Persists)
  │                 [Restart]            │
  │                    │                 │
  │  [Request image]   │                 │
  │ ← S3 URL ─────────←─────────────────│
  │ ← Image loads ✅                     │
  │
  Images persist forever!
```

---

## 🔧 How It Works

### Image Upload Process

```
1. User selects image in React app
   ↓
2. Frontend POST → /api/core/orders/
   ↓
3. Django receives file
   ↓
4. Model saves: order.image.save()
   ↓
5. django-storages intercepts (USE_S3=True)
   ↓
6. Uploads to S3 using AWS credentials
   ↓
7. S3 returns full URL
   ↓
8. Serializer returns JSON with image_url
   ↓
9. Frontend displays image from S3
   ↓
✅ Image persists across app restarts!
```

---

## 📊 Key Technical Details

### Environment-Based Behavior

```python
if USE_S3:
    # Production on Koyeb
    STORAGES = {
        'default': S3Boto3Storage,  # Media uploads go to S3
        'staticfiles': S3StaticStorage  # Static files on S3
    }
    MEDIA_URL = 'https://ultamine-media.s3.amazonaws.com/media/'
else:
    # Local development
    MEDIA_ROOT = BASE_DIR / 'media'  # Files stored locally
    MEDIA_URL = '/media/'  # Served by Django
```

### Models with Images
- `Deposit.deposit_proof` → `media/deposit_proofs/`
- `Product.image` → `media/products/`
- `ProductImage.image` → `media/products/`
- `Order.txid_proof` → `media/txid_proofs/`

### How URLs Are Returned
```python
# In serializers, image URLs become:

# Local development:
# /media/products/image.jpg
#    ↓ (serializer adds base URL)
# http://localhost:8000/media/products/image.jpg

# Koyeb with S3:
# https://ultamine-media.s3.amazonaws.com/media/products/image.jpg
#    ↓ (already full URL, returned as-is)
# https://ultamine-media.s3.amazonaws.com/media/products/image.jpg
```

---

## ✅ Success Criteria

When setup is complete:
- ✅ Can upload images without error
- ✅ Files appear in AWS S3 bucket
- ✅ Images display in your React app
- ✅ Images still exist after app restart
- ✅ Image URLs point to S3 domain
- ✅ No 404 or 403 errors
- ✅ No CORS errors in console

---

## 🆘 Troubleshooting Quick Ref

| Error | Cause | Fix |
|-------|-------|-----|
| 403 Forbidden | S3 not public | Uncheck "Block all public access" |
| 404 Not Found | Wrong bucket name | Verify AWS_STORAGE_BUCKET_NAME |
| CORS error | S3 CORS not set | Configure CORS in bucket |
| Upload fails | Bad AWS credentials | Check env vars in Koyeb |
| Wrong URL | S3 domain incorrect | Verify AWS_S3_CUSTOM_DOMAIN |

---

## 📝 Checklist

### AWS Setup
- [ ] S3 bucket created (`ultamine-media`)
- [ ] Public access disabled (allow)
- [ ] CORS configured
- [ ] IAM user created
- [ ] Access keys generated and saved

### Koyeb Configuration
- [ ] `USE_S3=True` added
- [ ] `AWS_ACCESS_KEY_ID` added
- [ ] `AWS_SECRET_ACCESS_KEY` added
- [ ] `AWS_STORAGE_BUCKET_NAME` added
- [ ] `AWS_S3_REGION_NAME` added

### Testing
- [ ] App redeployed
- [ ] Image uploaded
- [ ] File in S3 bucket
- [ ] Image displays
- [ ] App restarted
- [ ] Image still visible

---

## 🎓 Learning Resources

### Visual Learners
→ [IMAGE_UPLOAD_FLOW.md](IMAGE_UPLOAD_FLOW.md) - ASCII diagrams

### Code Learners
→ [IMAGE_URL_GENERATION.md](IMAGE_URL_GENERATION.md) - Code examples

### Step-by-Step Learners
→ [KOYEB_SETUP_CHECKLIST.md](KOYEB_SETUP_CHECKLIST.md) - Every click documented

### Just Tell Me What to Do
→ [KOYEB_QUICK_FIX.md](KOYEB_QUICK_FIX.md) - Minimal steps

---

## 💡 Pro Tips

1. **Bucket naming** - Must be globally unique, use lowercase + dashes
2. **Region** - Use same region for Koyeb and S3 for speed
3. **Cost** - ~$0.023/GB/month, very cheap for web app files
4. **Security** - Never commit AWS keys, always use env variables
5. **Monitoring** - Check S3 storage monthly to manage costs
6. **Scaling** - S3 handles unlimited uploads, perfect for scaling

---

## 🚀 Summary of What Changed

### Backend Code (Settings)
```python
# ✅ Updated config/settings.py
if USE_S3:
    STORAGES = {
        'default': S3Boto3Storage,
        'staticfiles': S3StaticStorage
    }
    MEDIA_URL = 'https://bucket.s3.amazonaws.com/media/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
```

### No Code Changes Needed on Your Part!
- ✅ All configuration is environment-variable based
- ✅ Works with existing database
- ✅ No migrations needed
- ✅ Backwards compatible with local development

---

## 📞 Get Help

### If stuck on AWS setup:
→ [KOYEB_S3_SETUP.md](KOYEB_S3_SETUP.md) Detailed steps with screenshots info

### If stuck on Koyeb config:
→ [.env.koyeb.example](.env.koyeb.example) Example env file

### If stuck on troubleshooting:
→ [KOYEB_SETUP_CHECKLIST.md](KOYEB_SETUP_CHECKLIST.md) Troubleshooting section

### If want to understand code:
→ [IMAGE_URL_GENERATION.md](IMAGE_URL_GENERATION.md) Code walkthrough

---

## ⏱️ Time Breakdown

| Task | Time |
|------|------|
| AWS S3 bucket setup | 5 min |
| AWS IAM user setup | 5 min |
| CORS configuration | 2 min |
| Environment variables | 5 min |
| Code deployment | 5 min |
| Testing | 5 min |
| **TOTAL** | **27 min** |

*Plus 10-15 min if you read the docs first*

---

## 🎉 You're Ready!

### Next Step:
1. Pick a guide (see above)
2. Follow the steps
3. Test it works
4. Celebrate! 🎊

### Start with:
**→ [KOYEB_QUICK_FIX.md](KOYEB_QUICK_FIX.md)** (fastest)

or

**→ [KOYEB_SETUP_CHECKLIST.md](KOYEB_SETUP_CHECKLIST.md)** (most detailed)

---

## 🔗 All Files Created

```
ultraminebackend/
├── KOYEB_IMAGE_FIX_COMPLETE.md ← You are here
├── README_KOYEB_IMAGE_FIX.md (index)
├── KOYEB_QUICK_FIX.md (5-step quick)
├── KOYEB_SETUP_CHECKLIST.md (detailed)
├── KOYEB_S3_SETUP.md (AWS setup)
├── IMAGE_URL_GENERATION.md (code)
├── IMAGE_UPLOAD_FLOW.md (diagrams)
├── KOYEB_IMPLEMENTATION_SUMMARY.md (what changed)
├── STATIC_FILES_SETUP.md (CSS/JS files)
├── .env.koyeb.example (env template)
├── setup_koyeb_s3.sh (Linux setup)
├── setup_koyeb_s3.ps1 (Windows setup)
├── config/
│   ├── settings.py ✅ Updated
│   └── urls.py ✅ Updated
└── requirements.txt ✅ Has django-storages
```

---

## 🎯 Final Checklist

Before you start:
- [ ] Read this file (you just did! ✓)
- [ ] Choose a guide from above
- [ ] Create AWS account (if needed)
- [ ] Follow the steps
- [ ] Test it works
- [ ] Celebrate! 🎉

---

## 🌟 Key Takeaway

**Problem:** Images disappear on Koyeb ❌  
**Solution:** Store on AWS S3 ✅  
**Effort:** 30 minutes ⏱️  
**Cost:** $0.023/GB/month 💰  
**Result:** Images persist forever! 🎉

---

**Ready? → Pick a guide and get started!** 🚀
