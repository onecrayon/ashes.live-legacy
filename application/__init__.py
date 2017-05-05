import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


# TODO: setup logging

current_path = os.path.dirname(os.path.abspath(__file__))

# Configure our app
app = Flask(
    __name__,
    static_folder=os.path.join(current_path, 'static'),
    template_folder=os.path.join(current_path, 'templates')
)

# Configure our application
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
app.config['ENVIRONMENT'] = ENVIRONMENT
app.config.from_pyfile('../config/config.py')
app.config.from_pyfile('../config/{}/config.py'.format(ENVIRONMENT))

# Configure our database
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
