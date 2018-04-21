from datetime import datetime
from random import choice
import re
import string
import uuid

from flask_login.mixins import UserMixin

from app import db, bcrypt


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    # Usernames are not unique, but the randomly-generated badge is; e.g. "Skaak#4eh?"
    badge = db.Column(db.String(8), unique=True, nullable=False, index=True)
    username = db.Column(db.String(42), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_banned = db.Column(db.Boolean, nullable=False, default=False)
    moderation_notes = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=False)
    reset_uuid = db.Column(db.String(36), nullable=True, default=None, index=True, unique=True)
    newsletter_opt_in = db.Column(db.Boolean, nullable=False, default=False)
    exclude_subscriptions = db.Column(db.Boolean, nullable=False, default=False)
    email_subscriptions = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, email, password, badge=None, username=None, description=None,
                 newsletter_opt_in=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        if badge and re.search(r'^[0-9][a-z0-9*&+=-]+[a-z0-9*!]$', badge):
            self.badge = badge
        else:
            self.badge = User.fetch_badges(True)
        self.username = username if username else choice([
            'Aradel Summergaard', 'Brennen Blackcloud', 'Coal Roarkwin',
            'Dimona Odinstar', 'Jessa Na Ni', 'Leo Sunshadow',
            'Lulu Firststone', 'Maeoni Viper', 'Namine Hymntide',
            'Noah Redmoon', 'Odette Diamondcrest', 'Orrick Gilstream',
            'Rin Northfell', 'Saria Guideman', 'Victoria Glassfire',
            'Echo Greystorm', 'Jericho Kill', 'Astrea', 'Koji Wolfcub'
        ])
        self.description = description
        self.newsletter_opt_in = newsletter_opt_in

    def generate_reset_uuid(self):
        # Grab a unique UUID
        str_id = str(uuid.uuid4())
        while User.query.filter(User.reset_uuid == str_id).first():
            str_id = str(uuid.uuid4())
        self.reset_uuid = str_id
        db.session.commit()

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)
        self.reset_uuid = None
        db.session.commit()

    @staticmethod
    def log_in(email, password):
        user =  User.query.filter(
            User.email == email
        ).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            return None
        return user
    
    @staticmethod
    def fetch_badges(single=False, number=8, length=4, _tries=1, _current=None):
        """Generates a list of user badges
        
        * `single`: if True, returns a single badge
        * `number`: number of badges to generate
        * `length`: the length of each individual badge
        * `_tries`: do not set; used internally to track recursion on failure
        * `_current`: do not set; used internally
        """
        # Increase the length if we failed to find badges 10 times in a row
        if _tries > 10:
            return User.fetch_badges(single, number, length=length+1)
        # Generate our badges
        options = generate_badges(number=number, length=length)
        # Test for kid-friendliness
        options = [x for x in options if kid_friendly(x)]
        # Highly unlikely, but if *all* options were bad, try again
        if not options:
            return User.fetch_badges(single, number, length, _tries=_tries+1, _current=_current)
        taken = [
            badge for (badge,) in db.session.query(User.badge).filter(User.badge.in_(options)).all()
        ]
        if taken:
            options = [x for x in options if x not in taken]
        # Highly unlikely, but if all random badges are taken, try again
        if not options:
            return User.fetch_badges(single, number, length, _tries=_tries+1, _current=_current)
        # Add pre-located options to our list
        if _current:
            options = _current + options
        # If we had to discard some, generate some more to fill in the gaps
        if len(options) < number:
            return User.fetch_badges(False, number, length, _tries=_tries+1,  _current=options)
        return options[0] if single else options[:number]


def generate_badges(number=8, length=4):
    return [''.join([
        # First character is always a number
        choice(string.digits),
        # Next characters are alphanumeric or middle punctuation
        ''.join(choice(string.ascii_lowercase + string.digits + '*&-+=') for _ in range(length-2)),
        # Final character alphanumeric or ending punctuation
        choice(string.ascii_lowercase + string.digits + '*!')
    ]) for _ in range(number)]


def kid_friendly(badge):
    return kid_unfriendly_re.search(badge) is None


# This is compiled based on data and logic from _assets/xxx-blacklist.txt
kid_unfriendly_re = re.compile(
	r'2(?:g|6)1(?:c|k)|(?:a|\*|@)n(?:a|\*|@)(?:i|\*|l|!|1)|(?:a|\*|@)n(?:u|\*|v)(?:s|\$|5|z|2)'
	r'|(?:a|\*|@)(?:s|\$|5|z|2)(?:s|\$|5|z|2)|(?:b|l3|i3)(?:b|l3|i3)(?:w|vv)|(?:b|l3|i3)d(?:s|\$|5|z|2)m'
	r'|(?:b|l3|i3)(?:i|\*|l|!|1)m(?:b|l3|i3)(?:o|\*|0)|(?:b|l3|i3)(?:i|\*|l|!|1)(?:t|7)(?:c|k)h'
	r'|(?:b|l3|i3)(?:o|\*|0)n(?:e|\*|3)r|(?:b|l3|i3)(?:o|\*|0)(?:o|\*|0)(?:b|l3|i3)'
	r'|(?:b|l3|i3)(?:u|\*|v)(?:t|7)(?:t|7)|(?:c|k)(?:i|\*|l|!|1)(?:i|\*|l|!|1)(?:t|7)'
	r'|(?:c|k)(?:o|\*|0)(?:c|k)(?:c|k)|(?:c|k)(?:o|\*|0)(?:o|\*|0)n|(?:c|k)(?:u|\*|v)m|(?:c|k)(?:u|\*|v)n(?:t|7)'
	r'|d(?:i|\*|l|!|1)(?:c|k)(?:c|k)|d(?:i|\*|l|!|1)(?:i|\*|l|!|1)d(?:o|\*|0)|d(?:o|\*|0)mm(?:e|\*|3)(?:s|\$|5|z|2)'
	r'|d(?:u|\*|v)d(?:a|\*|@)|(?:e|\*|3)(?:c|k)(?:c|k)h(?:i|\*|l|!|1)|(?:f|ph)(?:a|\*|@)(?:g|6)'
	r'|(?:f|ph)(?:e|\*|3)(?:c|k)(?:a|\*|@)(?:i|\*|l|!|1)|(?:f|ph)(?:e|\*|3)(?:i|\*|l|!|1)(?:c|k)h'
	r'|(?:f|ph)(?:e|\*|3)(?:i|\*|l|!|1)(?:t|7)(?:c|k)h|(?:f|ph)(?:e|\*|3)md(?:o|\*|0)m'
	r'|(?:f|ph)(?:u|\*|v)(?:c|k)(?:c|k)|(?:g|6)-(?:s|\$|5|z|2)p(?:o|\*|0)(?:t|7)|(?:g|6)(?:a|\*|@)y'
	r'|(?:g|6)(?:o|\*|0)(?:a|\*|@)(?:t|7)(?:c|k)x|(?:g|6)(?:o|\*|0)(?:a|\*|@)(?:t|7)(?:s|\$|5|z|2)(?:e|\*|3)'
	r'|(?:g|6)(?:o|\*|0)(?:c|k)(?:c|k)(?:u|\*|v)n|(?:g|6)r(?:o|\*|0)p(?:e|\*|3)'
	r'|(?:g|6)(?:s|\$|5|z|2)p(?:o|\*|0)(?:t|7)|(?:g|6)(?:u|\*|v)r(?:o|\*|0)'
	r'|h(?:e|\*|3)n(?:t|7)(?:a|\*|@)(?:i|\*|l|!|1)|h(?:o|\*|0)m(?:o|\*|0)|h(?:o|\*|0)n(?:c|k)(?:e|\*|3)y'
	r'|h(?:o|\*|0)(?:o|\*|0)(?:c|k)(?:e|\*|3)r|h(?:u|\*|v)mp|(?:i|\*|l|!|1)n(?:c|k)(?:e|\*|3)(?:s|\$|5|z|2)(?:t|7)'
	r'|j(?:i|\*|l|!|1)(?:s|\$|5|z|2)(?:s|\$|5|z|2)|j(?:u|\*|v)(?:g|6)(?:g|6)(?:s|\$|5|z|2)'
	r'|(?:c|k)(?:i|\*|l|!|1)(?:c|k)(?:e|\*|3)|(?:c|k)(?:i|\*|l|!|1)n(?:c|k)y'
	r'|(?:i|\*|l|!|1)(?:o|\*|0)(?:i|\*|l|!|1)(?:i|\*|l|!|1)(?:t|7)(?:a|\*|@)|m(?:i|\*|l|!|1)(?:i|\*|l|!|1)(?:f|ph)'
	r'|n(?:a|\*|@)m(?:b|l3|i3)(?:i|\*|l|!|1)(?:a|\*|@)|n(?:a|\*|@)(?:w|vv)(?:a|\*|@)(?:s|\$|5|z|2)h(?:i|\*|l|!|1)'
	r'|n(?:a|\*|@)(?:s|\$|5|z|2)(?:i|\*|l|!|1)|n(?:e|\*|3)(?:g|6)r(?:o|\*|0)'
	r'|n(?:e|\*|3)(?:o|\*|0)n(?:a|\*|@)(?:s|\$|5|z|2)(?:i|\*|l|!|1)|n(?:i|\*|l|!|1)(?:g|6)(?:g|6)(?:a|\*|@)'
	r'|n(?:i|\*|l|!|1)(?:g|6)(?:g|6)(?:e|\*|3)r|n(?:i|\*|l|!|1)pp(?:i|\*|l|!|1)(?:e|\*|3)|n(?:u|\*|v)d(?:e|\*|3)'
	r'|n(?:u|\*|v)d(?:i|\*|l|!|1)(?:t|7)y|nymph(?:o|\*|0)|(?:o|\*|0)r(?:g|6)(?:a|\*|@)(?:s|\$|5|z|2)m'
	r'|(?:o|\*|0)r(?:g|6)y|p(?:a|\*|@)(?:c|k)(?:i|\*|l|!|1)'
	r'|p(?:a|\*|@)n(?:t|7)(?:i|\*|l|!|1)(?:e|\*|3)(?:s|\$|5|z|2)|p(?:a|\*|@)n(?:t|7)y|p(?:e|\*|3)d(?:o|\*|0)'
	r'|p(?:e|\*|3)n(?:i|\*|l|!|1)(?:s|\$|5|z|2)|p(?:i|\*|l|!|1)(?:s|\$|5|z|2)(?:s|\$|5|z|2)'
	r'|p(?:o|\*|0)(?:o|\*|0)(?:f|ph)|p(?:o|\*|0)(?:o|\*|0)n|p(?:o|\*|0)(?:o|\*|0)p|p(?:o|\*|0)rn'
	r'|p(?:t|7)h(?:c|k)|p(?:u|\*|v)(?:b|l3|i3)(?:e|\*|3)(?:s|\$|5|z|2)|p(?:u|\*|v)(?:s|\$|5|z|2)(?:s|\$|5|z|2)y'
	r'|(?:q|9)(?:u|\*|v)(?:e|\*|3)(?:a|\*|@)(?:f|ph)|(?:q|9)(?:u|\*|v)(?:e|\*|3)(?:e|\*|3)(?:f|ph)'
	r'|(?:q|9)(?:u|\*|v)(?:i|\*|l|!|1)m|r(?:a|\*|@)p(?:e|\*|3)|r(?:a|\*|@)p(?:i|\*|l|!|1)n(?:g|6)'
	r'|r(?:a|\*|@)p(?:i|\*|l|!|1)(?:s|\$|5|z|2)(?:t|7)|r(?:e|\*|3)(?:c|k)(?:t|7)(?:u|\*|v)m'
	r'|r(?:i|\*|l|!|1)mj(?:o|\*|0)(?:b|l3|i3)|(?:s|\$|5|z|2)&m'
	r'|(?:s|\$|5|z|2)(?:a|\*|@)d(?:i|\*|l|!|1)(?:s|\$|5|z|2)m|(?:s|\$|5|z|2)(?:c|k)(?:a|\*|@)(?:t|7)'
	r'|(?:s|\$|5|z|2)(?:c|k)h(?:i|\*|l|!|1)(?:o|\*|0)n(?:g|6)|(?:s|\$|5|z|2)(?:e|\*|3)m(?:e|\*|3)n'
	r'|(?:s|\$|5|z|2)(?:e|\*|3)x|(?:s|\$|5|z|2)(?:e|\*|3)x(?:o|\*|0)|(?:s|\$|5|z|2)(?:e|\*|3)xy'
	r'|(?:s|\$|5|z|2)h(?:e|\*|3)m(?:a|\*|@)(?:i|\*|l|!|1)(?:e|\*|3)|(?:s|\$|5|z|2)h(?:i|\*|l|!|1)(?:t|7)'
	r'|(?:s|\$|5|z|2)h(?:o|\*|0)(?:t|7)(?:a|\*|@)|(?:s|\$|5|z|2)(?:c|k)(?:e|\*|3)(?:e|\*|3)(?:t|7)'
	r'|(?:s|\$|5|z|2)(?:i|\*|l|!|1)(?:u|\*|v)(?:t|7)|(?:s|\$|5|z|2)m(?:u|\*|v)(?:t|7)'
	r'|(?:s|\$|5|z|2)n(?:a|\*|@)(?:t|7)(?:c|k)h|(?:s|\$|5|z|2)(?:o|\*|0)d(?:o|\*|0)my'
	r'|(?:s|\$|5|z|2)p(?:i|\*|l|!|1)(?:c|k)|(?:s|\$|5|z|2)p(?:i|\*|l|!|1)(?:o|\*|0)(?:o|\*|0)(?:g|6)(?:e|\*|3)'
	r'|(?:s|\$|5|z|2)p(?:o|\*|0)(?:o|\*|0)(?:g|6)(?:e|\*|3)|(?:s|\$|5|z|2)p(?:u|\*|v)n(?:c|k)'
	r'|(?:s|\$|5|z|2)(?:t|7)r(?:i|\*|l|!|1)p|(?:s|\$|5|z|2)(?:u|\*|v)(?:c|k)(?:c|k)|(?:t|7)(?:i|\*|l|!|1)(?:t|7)'
	r'|(?:t|7)r(?:a|\*|@)nny|(?:t|7)(?:u|\*|v)(?:s|\$|5|z|2)hy|(?:t|7)(?:w|vv)(?:a|\*|@)(?:t|7)'
	r'|(?:t|7)(?:w|vv)(?:i|\*|l|!|1)n(?:c|k)|(?:u|\*|v)r(?:e|\*|3)(?:t|7)hr(?:a|\*|@)'
	r'|(?:u|\*|v)(?:a|\*|@)(?:g|6)(?:i|\*|l|!|1)n(?:a|\*|@)|(?:u|\*|v)(?:o|\*|0)y(?:e|\*|3)(?:u|\*|v)r'
	r'|(?:u|\*|v)(?:u|\*|v)(?:i|\*|l|!|1)(?:u|\*|v)(?:a|\*|@)|(?:w|vv)(?:a|\*|@)n(?:c|k)'
	r'|(?:w|vv)h(?:o|\*|0)r(?:e|\*|3)|y(?:a|\*|@)(?:o|\*|0)(?:i|\*|l|!|1)|y(?:i|\*|l|!|1)(?:f|ph)(?:f|ph)y'
)
