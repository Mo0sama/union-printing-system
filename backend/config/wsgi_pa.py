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

required_vars = ['DJANGO_SECRET_KEY', 'PA_DOMAIN']
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    raise RuntimeError(
        f'Missing required environment variables: {", ".join(missing)}. '
        f'Set them in {env_path} or as PA secrets.'
    )

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.production_settings'

if not os.environ.get('PA_DOMAIN'):
    raise RuntimeError('PA_DOMAIN environment variable must be set')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
