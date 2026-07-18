from .base import *
import dj_database_url
import logging
print('using prod settings')

DEBUG = False

db_url = os.environ["DATABASE_URL"]
DATABASES = {"default": dj_database_url.parse(db_url, engine='django.db.backends.postgresql')}

ALLOWED_HOSTS = ['swupharmacy-production.up.railway.app']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True

# DEFAULT_FROM_EMAIL = 'support@contactcorrector.com'

# AWS_SES_RETURN_PATH = 'lewis@contactcorrector.com'

# EMAIL_BACKEND = 'django_ses.SESBackend'

# AWS_SES_REGION_NAME = 'us-west-2'

# AWS_SES_REGION_ENDPOINT = 'email.us-west-2.amazonaws.com'

# SERVER_EMAIL = 'admin@contactcorrector.com'

ADMINS = [
    ('Lewis Fletcher', 'lew.fletcher3@gmail.com'),
]

CSRF_TRUSTED_ORIGINS = ['https://swupharmacy-production.up.railway.app']
'''
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''
'''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,  # Include HTML version of error emails
        },
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)