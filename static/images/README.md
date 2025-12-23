# Images Directory

This directory contains static image files used in the Django application.

## Usage

Place image files here and reference them in your templates:

```html
{% load static %}
<img src="{% static 'images/logo.png' %}" alt="Logo">
```

Or in REST API responses:
- URL: `/static/images/your-image.png`
- Example: `/static/images/logo.png`

## Supported Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- WebP (.webp)
- SVG (.svg)
- GIF (.gif)

## Optimization Tips

1. Compress images before uploading
2. Use WebP format for modern browsers
3. Provide fallbacks for older formats
4. Use descriptive filenames
5. Keep image sizes reasonable for web
