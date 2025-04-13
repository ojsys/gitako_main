import os
import sys

# Add the project directory to the sys.path
sys.path.insert(0, '/home/username/gitako_main')

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'gitako.settings.production'

# Import the WSGI application
from gitako.wsgi import application