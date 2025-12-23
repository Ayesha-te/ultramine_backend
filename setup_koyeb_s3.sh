#!/bin/bash
# Koyeb S3 Setup Helper Script
# Run this locally before deploying to Koyeb

echo "==================================="
echo "Koyeb S3 Setup Helper"
echo "==================================="
echo ""

# Check if django-storages is installed
python -c "import storages" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  django-storages not installed. Installing..."
    pip install django-storages[s3]
else
    echo "✓ django-storages is installed"
fi

echo ""
echo "Environment variables needed for Koyeb:"
echo "========================================"
echo "USE_S3=True"
echo "AWS_ACCESS_KEY_ID=your_access_key"
echo "AWS_SECRET_ACCESS_KEY=your_secret_key"
echo "AWS_STORAGE_BUCKET_NAME=your_bucket_name"
echo "AWS_S3_REGION_NAME=us-east-1"
echo ""

# Try to collect static files
echo "Attempting to collect static files..."
python manage.py collectstatic --noinput

echo ""
echo "✓ Setup complete!"
echo "Next steps:"
echo "1. Add the environment variables to your Koyeb project"
echo "2. Redeploy your application"
echo "3. Test image upload"
echo ""
echo "For detailed instructions, see KOYEB_S3_SETUP.md"
