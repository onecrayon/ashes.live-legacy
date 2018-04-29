from datetime import datetime

from app import db
from app.models.user import User


class Streamable(db.Model):
    """A Streamable entity is one that can show up in activity streams"""
    entity_id = db.Column(db.Integer, primary_key=True)


class Stream(db.Model):
    """Stream entries are used to construct activity streams"""
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True, unique=True)
    entity_type = db.Column(db.String(16))
    source_entity_id = db.Column(db.Integer, nullable=False, index=True)
    section_entity_id = db.Column(db.Integer, index=True)
    posted = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class Subscription(db.Model):
    """A Subscription subscribes a user to a Streamable entity's comments"""
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True, nullable=False)
    source_entity_id = db.Column(db.Integer, primary_key=True, nullable=False)
    last_seen_entity_id = db.Column(db.Integer, index=True)
