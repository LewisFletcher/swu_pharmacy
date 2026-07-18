from .base import os

if os.environ.get('DJANGO_ENV') == 'prod':
    from .prod import *
elif os.environ.get('DJANGO_ENV') == 'dev':
    from .dev import *
else:  # Defaults to production for security purposes
    from .prod import *