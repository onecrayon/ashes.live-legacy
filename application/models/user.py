from datetime import datetime

from flask_login.mixins import UserMixin
from application import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    # Usernames are not unique, but the randomly-generated badge is; e.g. "Skaak#4eh?"
    badge = db.Column(db.String(8), unique=True, nullable=False, index=True)
    username = db.Column(db.String(42), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
