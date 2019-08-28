SESSION_TYPE = 'sqlalchemy'
SESSION_USE_SIGNER = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
# Number of results to show in paginated responses
DEFAULT_PAGED_RESULTS = 10
COLLAPSED_PAGED_RESULTS = 20
# Timezone to output datetimes in
LOCAL_TZ = 'America/Los_Angeles'

### Environment-specific ###

# Site root URL; no trailing slash
SITE_URL = 'https://ashes.live'
# Root CDN URL; no trailing slash (leave empty for locally-hosted resources)
CDN_URL = ''

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
# Set to an email to have all site emails re-routed here when DEBUG == True above
DEBUG_MAIL_RECIPIENT = ''

# Optional; if set will use SendGrid instead of SMTP
SENDGRID_API_KEY = ''
