import os
import sys

sys.path.append(os.path.dirname(__file__))
os.environ['ENVIRONMENT'] = 'production'

# Import our WSGI application
from manager import app as application
