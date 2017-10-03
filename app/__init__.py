import json
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy


# TODO: setup logging

current_path = os.path.dirname(os.path.abspath(__file__))

# Configure our app
app = Flask(
    __name__,
    static_url_path='',
    static_folder=os.path.join(current_path, 'static'),
    template_folder=os.path.join(current_path, 'templates')
)

# Configure our application
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
app.config['ENVIRONMENT'] = ENVIRONMENT
app.config.from_pyfile('../config/config.py')
app.config.from_pyfile('../config/{}/config.py'.format(ENVIRONMENT))
# Load our version (to append to query strings)
package_json = json.load(open(os.path.join(current_path, '../package.json')))
app.config['VERSION'] = package_json['version']

# Configure our database
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# Configure our server-side sessions
app.config.from_mapping({
    'SESSION_SQLALCHEMY': db
})
Session(app)

# Configure login functionality
login_manager = LoginManager()
login_manager.init_app(app)

# Configure mailer
mail = Mail(app)

# Include template filters (this import requires app to be configured)
from app import template_filters  # noqa
