import os

# Load the appropriate settings based on the environment
environment = os.getenv('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *