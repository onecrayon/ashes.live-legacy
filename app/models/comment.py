from datetime import datetime

from app import db
from app.models.user import User


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    # This points to the entity_id being commented on
    source_entry_id = db.Column(db.Integer, nullable=False, index=True)
    source_type = db.Column(db.String(16))
    text = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
