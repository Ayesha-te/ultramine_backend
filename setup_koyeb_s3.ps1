# Koyeb S3 Setup Helper Script (PowerShell)
# Run this locally before deploying to Koyeb

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Koyeb S3 Setup Helper" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if django-storages is installed
try {
    python -c "import storages" 2>$null
    Write-Host "✓ django-storages is installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  django-storages not installed. Installing..." -ForegroundColor Yellow
    pip install "django-storages[s3]"
}

Write-Host ""
Write-Host "Environment variables needed for Koyeb:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "USE_S3=True"
Write-Host "AWS_ACCESS_KEY_ID=your_access_key"
Write-Host "AWS_SECRET_ACCESS_KEY=your_secret_key"
Write-Host "AWS_STORAGE_BUCKET_NAME=your_bucket_name"
Write-Host "AWS_S3_REGION_NAME=us-east-1"
Write-Host ""

# Try to collect static files
Write-Host "Attempting to collect static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

Write-Host ""
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Add the environment variables to your Koyeb project"
Write-Host "2. Redeploy your application"
Write-Host "3. Test image upload"
Write-Host ""
Write-Host "For detailed instructions, see KOYEB_S3_SETUP.md" -ForegroundColor Cyan
