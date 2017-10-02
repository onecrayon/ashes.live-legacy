SESSION_TYPE = 'sqlalchemy'
SESSION_USE_SIGNER = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
# Number of results to show in paginated responses
DEFAULT_PAGED_RESULTS = 10

### Environment-specific ###

# Site root URL; no trailing slash
SITE_URL = 'http://ashes.live'

# Flask
SECRET_KEY = ''
DEBUG = False

# Database
SQLALCHEMY_DATABASE_URI = ''

# Mail
MAIL_SERVER = ''
MAIL_PORT = 25
MAIL_USE_TLS = True
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = None
MAIL_MAX_EMAILS = None
