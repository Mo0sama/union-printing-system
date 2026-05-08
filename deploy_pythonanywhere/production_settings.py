import os
from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    os.environ.get('PA_DOMAIN', 'yourusername.pythonanywhere.com'),
    'localhost', '127.0.0.1',
]

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'change-this-to-a-real-random-secret-key-in-production'
)

# Static files (WhiteNoise)
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

# Security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True

# Language
LANGUAGE_CODE = 'ar'
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
