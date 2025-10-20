#!/bin/bash

# Exit on any error
set -e

echo "=== Starting Django Application Build ==="

# Install dependencies
echo "1. Installing Python dependencies..."
pip install -r requirements.txt

# Set Python path for Django
export PYTHONPATH="/var/task:$PYTHONPATH"
export DJANGO_SETTINGS_MODULE="waste_management.settings"

# Create necessary directories
echo "2. Creating static files directories..."
mkdir -p staticfiles
mkdir -p media

# Collect static files
echo "3. Collecting static files..."
python manage.py collectstatic --noinput --clear

# Skip migrations during build (run them at runtime instead)
echo "4. Skipping migrations during build (will run at runtime)..."

echo "=== Build completed successfully ==="
