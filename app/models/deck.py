from datetime import datetime

from app import db
from app.models.card import Card, Die
from app.models.user import User


decks_cards = db.Table(
    'decks_cards',
    db.Column('deck_id', db.Integer, db.ForeignKey('deck.id')),
    db.Column('card_id', db.Integer, db.ForeignKey(Card.id))
)


decks_dice = db.Table(
    'decks_dice',
    db.Column('deck_id', db.Integer, db.ForeignKey('deck.id')),
    db.Column('die_id', db.Integer, db.ForeignKey(Die.id))
)


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
    cards = db.relationship(Card, secondary=decks_cards)
    dice = db.relationship(Die, secondary=decks_dice)
