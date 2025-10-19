#!/bin/bash

echo "=== Starting Clean Uganda Build Process ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p staticfiles
mkdir -p media

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations (if needed)
# Note: For Vercel, you might want to run migrations separately
# echo "Running migrations..."
# python manage.py migrate --noinput

echo "=== Build completed successfully ==="