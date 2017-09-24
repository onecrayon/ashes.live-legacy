from datetime import datetime

from app import db
from app.models.card import Card
from app.models.user import User


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), index=True)
    description = db.Column(db.Text)
    public = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, index=True)
    phoenixborn_id = db.Column(db.Integer, db.ForeignKey(Card.id), index=True)
    
    user = db.relationship(User)
    phoenixborn = db.relationship(Card)
    # `cards` and `dice` are defined via backref in the models below


class DeckCard(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey(Deck.id), nullable=False, index=True)
    card_id = db.Column(db.Integer, db.ForeignKey(Card.id), nullable=False)
    count = db.Column(db.SmallInteger, nullable=False)

    card = db.relationship(Card)
    deck = db.relationship(Deck, backref='cards')


class DeckDie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey(Deck.id), nullable=False, index=True)
    die_flag = db.Column(db.Integer, nullable=False)
    count = db.Column(db.SmallInteger, nullable=False)

    deck = db.relationship(Deck, backref='dice')
