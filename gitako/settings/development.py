from .base import *

DEBUG = True

# Development-specific settings
INSTALLED_APPS += [
    'django_extensions',
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'