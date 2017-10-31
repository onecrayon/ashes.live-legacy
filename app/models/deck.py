from datetime import datetime

from app import db
from app.models.card import Card
from app.models.user import User


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), index=True)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_snapshot = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    # Snapshots will always have a deck as their source; decks can be sourced from a private
    # snapshot (if the two share a user_id) or any public snapshot
    source_id = db.Column(db.Integer, db.ForeignKey('deck.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, index=True)
    phoenixborn_id = db.Column(db.Integer, db.ForeignKey(Card.id), index=True)
    
    user = db.relationship(User)
    phoenixborn = db.relationship(Card)
    source = db.relationship('Deck')
    # `cards` and `dice` are defined via backref in the models below

    def public_snapshots(self, limit=None):
        if self.is_snapshot:
            return None
        query = Deck.query.filter(
            Deck.source_id == self.id,
            Deck.is_snapshot.is_(True),
            Deck.is_public.is_(True)
        ).order_by(Deck.created.desc())
        if limit:
            query = query.limit(limit)
        return query.all()


class DeckCard(db.Model):
    deck_id = db.Column(db.Integer, db.ForeignKey(Deck.id), nullable=False, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey(Card.id), nullable=False, primary_key=True)
    count = db.Column(db.SmallInteger, nullable=False)

    card = db.relationship(Card)
    deck = db.relationship(
        Deck,
        backref=db.backref('cards', cascade='all, delete-orphan')
    )


class DeckDie(db.Model):
    deck_id = db.Column(db.Integer, db.ForeignKey(Deck.id), nullable=False, primary_key=True)
    die_flag = db.Column(db.Integer, nullable=False, primary_key=True)
    count = db.Column(db.SmallInteger, nullable=False)

    deck = db.relationship(
        Deck,
        backref=db.backref('dice', cascade='all, delete-orphan')
    )
