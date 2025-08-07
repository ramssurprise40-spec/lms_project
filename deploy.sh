# LMS Deployment Script for Windows (Development Mode)
# Note: This uses Django's built-in runserver (not for production).

Write-Host "🚀 Starting LMS deployment (Windows)..."

# Exit on error
$ErrorActionPreference = "Stop"

# Check if manage.py exists
if (-Not (Test-Path "manage.py")) {
    Write-Host "❌ Error: manage.py not found. Make sure you're in the project root directory."
    exit 1
}

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found. Copy .env.example to .env and configure it."
    exit 1
}

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies and build CSS
Write-Host "🎨 Building frontend assets..."
npm install
npm run build

# Run Django checks
Write-Host "🔍 Running Django system checks..."
python manage.py check

# Collect static files
Write-Host "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
Write-Host "🔄 Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
Write-Host "👤 Creating superuser (if needed)..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', input('Enter admin password: '))"

# Start Django development server
Write-Host "🚀 Starting Django development server (http://127.0.0.1:8000)..."
python manage.py runserver
