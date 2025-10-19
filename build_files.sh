#!/bin/bash

echo "=== Starting Clean Uganda Build Process ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p staticfiles
mkdir -p media

# Make Django migrations for all apps
echo "Creating migrations..."
python3 manage.py makemigrations --noinput

# Run database migrations
echo "Running migrations..."
python3 manage.py migrate --noinput

# Create superuser if needed (optional)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'password') if not User.objects.filter(username='admin').exists() else None" | python3 manage.py shell

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Create the dist directory that Vercel expects
echo "Creating dist directory..."
mkdir -p dist
# Copy static files to dist directory for Vercel static build
cp -r staticfiles/* dist/ 2>/dev/null || true

echo "=== Build completed successfully ==="
