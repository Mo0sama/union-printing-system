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

# Session security
SESSION_COOKIE_AGE = 28800  # 8 hours
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

MIDDLEWARE.insert(1, 'csp.middleware.CSPMiddleware')

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

# django-axes: brute force protection
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.5  # 30 minutes
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_RESET_ON_SUCCESS = True

# CSP (django-csp v4.x format)
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "style-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com", "https://fonts.gstatic.com"],
        "script-src": ["'self'", "https://cdn.jsdelivr.net", "https://code.jquery.com"],
        "font-src": ["'self'", "https://cdn.jsdelivr.net", "https://fonts.gstatic.com"],
        "img-src": ["'self'", "data:", "blob:"],
        "connect-src": ["'self'"],
    }
}

# Email: use SMTP only if credentials are configured in .env
# Free PythonAnywhere blocks outbound SMTP, so defaults to console
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@unionprinting.com')

_LOGS_DIR = BASE_DIR / 'logs'
_LOGS_DIR.mkdir(exist_ok=True)

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
            'filename': _LOGS_DIR / 'django_errors.log',
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
