from app import db
from app.models.card import Card


class Ashes500Revision(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    description = db.Column(db.Text)


class Ashes500Value(db.Model):
    card_id = db.Column(db.Integer, db.ForeignKey(Card.id), nullable=False, primary_key=True)
    revision_id = db.Column(db.Integer, db.ForeignKey(Ashes500Revision.id), nullable=False,
                            primary_key=True, index=True)
    qty_1 = db.Column(db.SmallInteger, nullable=False)
    qty_2 = db.Column(db.SmallInteger, nullable=True)
    qty_3 = db.Column(db.SmallInteger, nullable=True)
