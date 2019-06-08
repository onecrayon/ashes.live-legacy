from datetime import datetime

from app import db


class PhoenixDice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    only_official_icons = db.Column(db.Boolean, nullable=False, default=False, index=True)
    desired_sets = db.Column(db.Integer, nullable=False, default=1)
    created = db.Column(db.DateTime, default=datetime.utcnow)
