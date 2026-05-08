import os
import sys

# Add your project directory to sys.path
path = '/home/yourusername/union-printing-system/backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.production_settings'

# Set your PythonAnywhere domain (for ALLOWED_HOSTS)
os.environ['PA_DOMAIN'] = 'yourusername.pythonanywhere.com'

# Load Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
