import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waste_management.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    # If there's an error, print it but don't crash
    print(f"Error initializing Django: {e}")
    raise
