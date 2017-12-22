SESSION_TYPE = 'sqlalchemy'
SESSION_USE_SIGNER = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
# Number of results to show in paginated responses
DEFAULT_PAGED_RESULTS = 10
# Timezone to output datetimes in
LOCAL_TZ = 'America/Los_Angeles'

### Global configuration options ###
RELEASE_NAMES = {
    0: 'Core Set',
    1: 'The Frostdale Giants',
    2: 'The Children of Blackcloud',
    3: 'The Roaring Rose',
    4: 'The Duchess of Deception',
    5: 'The Laws of Lions',
    6: 'The Song of Soaksend',
    7: 'The Masters of Gravity',
    8: 'The Path of Assassins',
    9: 'The Goddess of Ishra',
    10: 'The Boy Among Wolves',
    101: 'Dimona Odinstar (promo)',
    102: 'Lulu Firststone (promo)',
    103: 'Orrick Gilstream (promo)'
}

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
