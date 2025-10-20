from http.server import BaseHTTPRequestHandler
import os
import sys
import django
from django.core.management import execute_from_command_line

# Add your project to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waste_management.settings')

django.setup()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Run migrations
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Migrations completed successfully')
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Migration failed: {str(e)}'.encode())