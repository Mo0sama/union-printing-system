import os
import sys
from pathlib import Path

from dotenv import load_dotenv

path = '/home/mossama/union-printing-system/backend'
if path not in sys.path:
    sys.path.insert(0, path)

env_path = Path(path) / '.env'
if env_path.exists():
    load_dotenv(env_path)

os.environ.setdefault('DJANGO_SECRET_KEY', 'DYhN1YKUWkwygrbuRWV86qnxQLS8ttixddY3L1KhdDWs6rpzEBt2U84e3ImxJkUlIH0')

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.production_settings'
os.environ['PA_DOMAIN'] = 'mossama.pythonanywhere.com'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
