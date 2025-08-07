# Development management script for Windows PowerShell
# Usage: .\manage_dev.ps1 <command>

param(
    [string]$Command = "help"
)

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

switch ($Command) {
    "setup" {
        Write-Host "Setting up development environment..."
        pip install -r requirements.txt
        npm install
        python manage.py migrate
        Write-Host "Development setup complete!"
    }
    "run" {
        Write-Host "Starting development server..."
        Start-Process powershell -ArgumentList "-Command", "npm run dev"
        python manage.py runserver
    }
    "migrate" {
        python manage.py makemigrations
        python manage.py migrate
    }
    "test" {
        pytest
    }
    "lint" {
        flake8 .
        black --check .
        isort --check-only .
    }
    "format" {
        black .
        isort .
    }
    "build" {
        npm run build
        python manage.py collectstatic --noinput
    }
    "help" {
        Write-Host "Available commands:"
        Write-Host "  setup   - Set up development environment"
        Write-Host "  run     - Run development server with CSS watching"
        Write-Host "  migrate - Run Django migrations"
        Write-Host "  test    - Run tests"
        Write-Host "  lint    - Check code quality"
        Write-Host "  format  - Format code"
        Write-Host "  build   - Build for production"
    }
    default {
        python manage.py $Command $args
    }
}
