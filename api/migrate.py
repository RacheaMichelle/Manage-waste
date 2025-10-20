from http.server import BaseHTTPRequestHandler
import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waste_management.settings')

import django
django.setup()

from django.core.management import execute_from_command_line

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        try:
            # Run migrations
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            self.wfile.write(b'Migrations completed successfully!')
        except Exception as e:
            self.wfile.write(f'Migration error: {str(e)}'.encode())
