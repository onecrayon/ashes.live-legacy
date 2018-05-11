from datetime import datetime

from sqlalchemy_fulltext import FullText

from app import db
from app.models.user import User


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True, unique=True)
    title = db.Column(db.String(255), nullable=False)
    stub = db.Column(db.String(255), nullable=False, index=True, unique=True)
    description = db.Column(db.Text)
    is_restricted = db.Column(db.Boolean, nullable=False, default=False, index=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey(Section.id), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text)
    pin_teaser = db.Column(db.Text)
    is_pinned = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_moderated = db.Column(db.Boolean, nullable=False, default=False)
    original_title = db.Column(db.String(255))
    original_text = db.Column(db.Text)
    moderation_notes = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship(User)
    section = db.relationship(Section)


class TitleTextSearch(FullText, Post):
    __fulltext_columns__ = ('title', 'text')
