import json
import os
from flask import Flask, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, logout_user
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

@app.before_request
def verify_user():
    if current_user.is_authenticated and current_user.is_banned:
        logout_user()
        flash(
            'Your account has been banned. If you wish to appeal the ban, '
            'please <a href="{}" class="error">contact me</a>.'.format(
                url_for('home.feedback')
            ),
            'error'
        )
        return redirect(url_for('home.index'))

# Include template filters (this import requires app to be configured)
from app import jinja_globals  # noqa
