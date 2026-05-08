import os
import sys

path = '/home/mossama/union-printing-system/backend'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.production_settings'
os.environ['PA_DOMAIN'] = 'mossama.pythonanywhere.com'

# IMPORTANT: Set DJANGO_SECRET_KEY in PythonAnywhere Web tab -> Environment variables
# Or uncomment below with a REAL random secret key:
# os.environ['DJANGO_SECRET_KEY'] = 'replace-with-a-real-random-secret-key'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
