#!/bin/bash

# Install Python dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run Django migrations
echo "Running database migrations..."
python manage.py migrate --noinput

echo "Build completed successfully!"