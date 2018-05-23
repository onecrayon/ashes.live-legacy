from datetime import datetime

from app import db
from app.models.card import Card


class Ashes500Revision(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    description = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class Ashes500Value(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, db.ForeignKey(Card.id), nullable=False, index=True)
    revision_id = db.Column(db.Integer, db.ForeignKey(Ashes500Revision.id), nullable=False,
                            index=True)
    combo_card_id = db.Column(db.Integer, db.ForeignKey(Card.id), nullable=True, default=None)
    qty_1 = db.Column(db.SmallInteger, nullable=False)
    qty_2 = db.Column(db.SmallInteger, nullable=True)
    qty_3 = db.Column(db.SmallInteger, nullable=True)
