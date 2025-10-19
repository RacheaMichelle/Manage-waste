#!/bin/bash

echo "=== Starting Clean Uganda Build Process ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p staticfiles
mkdir -p media

# Make Django migrations
echo "Creating migrations..."
python manage.py makemigrations users waste matching analytics education educ report chatbot

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "=== Build completed successfully ==="
