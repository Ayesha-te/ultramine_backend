# Django Static Files Setup Guide

## Configuration Overview

Your Django static files have been properly configured. Here's what was set up:

### 1. Settings Configuration (settings.py)

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (uploaded by users)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**What each setting does:**
- `STATIC_URL`: URL prefix for serving static files (e.g., `/static/`)
- `STATIC_ROOT`: Directory where `collectstatic` copies files for production
- `STATICFILES_DIRS`: Additional directories where static files are located during development
- `MEDIA_URL`: URL prefix for user-uploaded files
- `MEDIA_ROOT`: Directory where uploaded files are stored

### 2. URL Configuration (urls.py)

Development static files serving is configured in `urls.py`:

```python
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

This allows Django to serve static and media files automatically in development when `DEBUG=True`.

### 3. Directory Structure

Created folders for organizing static files:

```
ultraminebackend/
├── static/
│   ├── css/          # CSS stylesheets
│   ├── js/           # JavaScript files
│   └── images/       # Image files
├── media/            # User-uploaded files
├── staticfiles/      # Production static files (created by collectstatic)
└── config/
    ├── settings.py
    └── urls.py
```

## How to Use Static Files

### In Django Templates

If you have any Django templates, use the `{% static %}` template tag:

```html
{% load static %}

<img src="{% static 'images/logo.png' %}" alt="Logo">
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/main.js' %}"></script>
```

### Direct File Paths

Place your files in the corresponding directories:
- **CSS files**: `static/css/` → Access via `/static/css/style.css`
- **JavaScript files**: `static/js/` → Access via `/static/js/main.js`
- **Images**: `static/images/` → Access via `/static/images/logo.png`
- **User uploads**: `media/` → Access via `/media/filename.ext`

## Development vs Production

### Development
- Django automatically serves static files when `DEBUG=True`
- Files served directly from `STATICFILES_DIRS` and app static folders
- No need to run `collectstatic`

### Production
Before deploying to production:

```bash
python manage.py collectstatic --noinput
```

This gathers all static files from `STATICFILES_DIRS` and apps into `STATIC_ROOT` so your web server (Nginx, Gunicorn, etc.) can serve them.

## Troubleshooting

### 404 Errors on Static Files

1. **Check file path**: Ensure the file exists in the correct location
2. **Check URL**: Verify the URL in browser matches the file location
3. **Case sensitivity**: Linux servers are case-sensitive!
   - `/static/images/logo.png` ≠ `/static/images/Logo.png`
4. **DEBUG mode**: Ensure `DEBUG=True` in development
5. **STATIC_URL**: Make sure `STATIC_URL` starts with `/`

### S3 Integration (if enabled)

If `USE_S3=True`, static files are served from AWS S3:
- Ensure AWS credentials are set
- CORS configuration includes S3 bucket
- Files are stored in S3 bucket instead of local directory

### File Not Found in collectstatic

If `collectstatic` misses files:
1. Add the directory to `STATICFILES_DIRS`
2. Ensure the file path is correct
3. Check `.gitignore` isn't excluding files

## Quick Checklist

- [x] `STATIC_URL` configured with leading `/`
- [x] `STATIC_ROOT` set to `BASE_DIR / 'staticfiles'`
- [x] `STATICFILES_DIRS` includes `BASE_DIR / 'static'`
- [x] `MEDIA_URL` and `MEDIA_ROOT` configured
- [x] Static file serving enabled in `urls.py` for development
- [x] Directory structure created (css, js, images)
- [x] Case sensitivity considered for file names
