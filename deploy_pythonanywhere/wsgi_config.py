import os
import sys

# Add your project directory to sys.path
path = '/home/mossama/union-printing-system/backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.production_settings'

# Set your PythonAnywhere domain (for ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS)
os.environ['PA_DOMAIN'] = 'mossama.pythonanywhere.com'

# Set your secret key
os.environ['DJANGO_SECRET_KEY'] = 'your-random-secret-key-here'

# Load Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
