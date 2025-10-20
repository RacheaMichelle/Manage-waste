import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waste_management.settings')

# Initialize Django
application = get_wsgi_application()

# Run migrations on startup in production
if os.environ.get('VERCEL') == '1' and os.environ.get('DEBUG', 'False').lower() == 'false':
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("Database migrations completed on startup")
    except Exception as e:
        print(f"Migration error on startup: {e}")
