from datetime import datetime

from flask_login import current_user
from sqlalchemy.ext.hybrid import hybrid_property

from app import db
from app.models.card import Card
from app.models.user import User


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True, unique=True)
    title = db.Column(db.String(255), index=True)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_snapshot = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_preconstructed = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    # Snapshots will always have a deck as their source; decks can be sourced from a private
    # snapshot (if the two share a user_id) or any public snapshot
    source_id = db.Column(db.Integer, db.ForeignKey('deck.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, index=True)
    phoenixborn_id = db.Column(db.Integer, db.ForeignKey(Card.id), index=True)
    
    user = db.relationship(User)
    phoenixborn = db.relationship(Card)
    source = db.relationship('Deck', uselist=False, remote_side=[id])
    # `cards` and `dice` are defined via backref in the models below

    def published_snapshot(self, full=False):
        """Returns the ID or None for the most recent published snapshot"""
        if self.is_snapshot:
            return None
        query = db.session.query(Deck).filter(
            Deck.source_id == self.id,
            Deck.is_snapshot.is_(True),
            Deck.is_public.is_(True)
        ).order_by(Deck.created.desc())
        if full:
            query = query.options(
                db.joinedload('phoenixborn').joinedload('conjurations'),
                db.joinedload('cards').joinedload('card').joinedload('conjurations'),
                db.joinedload('dice'),
                db.joinedload('user'),
                db.joinedload('source').joinedload('phoenixborn')
            )
        return query.first()

    @hybrid_property
    def has_snapshots(self):
        """Returns True if the deck (or source, for snapshots) has visible snapshots."""
        if self.is_snapshot and (self.is_public or (
                current_user.is_authenticated and
                self.user_id == current_user.id)):
            return True
        source_id = self.id if not self.is_snapshot else self.source_id
        query = Deck.query.filter(
            Deck.is_snapshot.is_(True),
            Deck.source_id == source_id
        )
        if not current_user.is_authenticated or self.user_id != current_user.id:
            query = query.filter(Deck.is_public.is_(True))
        return query.count() > 0


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
