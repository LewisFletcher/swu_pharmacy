from .base import *
import logging
print('using dev settings')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'django_browser_reload', #tailwind reload
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

NPM_BIN_PATH = 'C:\\Program Files\\nodejs\\npm.cmd'

# Prod uses S3 (see base.py), but that requires django-storages plus real
# bucket credentials that aren't configured anywhere yet. Use local disk
# for dev so file uploads (e.g. prescription labels) actually work.
STORAGES['default'] = {'BACKEND': 'django.core.files.storage.FileSystemStorage'}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)