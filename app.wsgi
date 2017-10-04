import os


# Setup production environment
os.environ['ENVIRONMENT'] = 'production'

# Import our WSGI application
from manager import app as application
