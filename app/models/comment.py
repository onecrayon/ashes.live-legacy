from datetime import datetime
import math

from flask import current_app, url_for
from sqlalchemy.ext.hybrid import hybrid_property

from app import db
from app.models.card import Card
from app.models.deck import Deck
from app.models.user import User


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    # This points to the entity_id being commented on
    source_entity_id = db.Column(db.Integer, nullable=False, index=True)
    source_type = db.Column(db.String(16))
    source_version = db.Column(db.Integer)
    text = db.Column(db.Text)
    order = db.Column(db.Integer, index=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    is_moderated = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship(User)

    @hybrid_property
    def source(self):
        try:
            return self._source
        except AttributeError:
            if self.source_type == 'card':
                self._source = db.session.query(Card).filter(
                    Card.entity_id == self.source_entity_id
                ).first()
            elif self.source_type == 'deck':
                self._source = db.session.query(Deck).filter(
                    Deck.entity_id == self.source_entity_id
                ).first()
            return self._source

    @hybrid_property
    def url(self):
        """Returns the site URL for the given comment"""
        per_page = current_app.config['DEFAULT_PAGED_RESULTS']
        page = math.ceil(self.order / per_page)
        anchor = 'comment-{}'.format(self.id)
        if page == 1:
            page = None
        if self.source_type == 'card':
            return url_for('cards.detail', stub=self.source.stub, page=page, _anchor=anchor)
        elif self.source_type == 'deck':
            return url_for('decks.view', deck_id=self.source.id, page=page, _anchor=anchor)
