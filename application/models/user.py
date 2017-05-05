from datetime import datetime
from random import choice
import string

from flask_login.mixins import UserMixin
from application import db, bcrypt


def generate_badges(number=8, length=4):
    return [''.join([
        # First character is always a number
        choice(string.digits),
        # Next characters are alphanumeric or middle punctuation
        ''.join(choice(string.ascii_lowercase + string.digits + '*&-+=') for _ in range(length-2)),
        # Final character alphanumeric or ending punctuation
        choice(string.ascii_lowercase + string.digits + '*%!?')
    ]) for _ in range(number)]


def kid_friendly(badge):
    # TODO: actually test against a blacklist for non-kid-friendly words
    return True


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    # Usernames are not unique, but the randomly-generated badge is; e.g. "Skaak#4eh?"
    badge = db.Column(db.String(8), unique=True, nullable=False, index=True)
    username = db.Column(db.String(42), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, email, password, badge=None, username=None):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.badge = badge if badge else User.fetch_badges(True)
        self.username = username if username else choice([
            'Aradel Summergaard', 'Brennen Blackcloud', 'Coal Roarkwin',
            'Dimona Odinstar', 'Jessa Na Ni', 'Leo Sunshadow',
            'Lulu Firststone', 'Maeoni Viper', 'Namine Hymntide',
            'Noah Redmoon', 'Odette Diamondcrest', 'Orrick Gilstream',
            'Rin Northfell', 'Saria Guideman', 'Victoria Glassfire'
        ])
    
    @staticmethod
    def fetch_badges(single=False, maximum=8, length=4):
        options = generate_badges(number=maximum, length=length)
        # Test for kid-friendliness
        options = [x for x in options if kid_friendly(x)]
        # Highly unlikely, but if *all* options were bad, try again
        if not options:
            return User.fetch_badges(single, maximum, length)
        taken = [
            badge for (badge,) in db.session.query(User.badge).filter(User.badge.in_(options)).all()
        ]
        if taken:
            options = [x for x in options if x not in taken]
        # Highly unlikely, but if all random badges are taken, try again
        if not options:
            return User.fetch_badges(single, maximum, length)
        return options[0] if single else options
