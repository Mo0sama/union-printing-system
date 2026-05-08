# This is a reference/template file.
# The actual production settings live at:
#   backend/config/production_settings.py
#
# Copy this to PA and ensure DJANGO_SETTINGS_MODULE=config.production_settings
# and PA_DOMAIN + DJANGO_SECRET_KEY env vars are set on PythonAnywhere.

import os
from django.core.exceptions import ImproperlyConfigured
from .settings import *

DEBUG = False

PA_DOMAIN = os.environ.get('PA_DOMAIN')
if not PA_DOMAIN:
    raise ImproperlyConfigured('PA_DOMAIN environment variable must be set')

ALLOWED_HOSTS = [
    PA_DOMAIN,
    'localhost', '127.0.0.1',
]

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY environment variable must be set')

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = [f'https://{PA_DOMAIN}']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

LANGUAGE_CODE = 'ar'
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
