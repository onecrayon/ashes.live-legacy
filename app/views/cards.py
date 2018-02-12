"""Card gallery"""

import json

from flask import abort, current_app, Blueprint, render_template

from app import db
from app.models.card import Card
from app.models.deck import Deck, DeckCard
from app.utils.cards import global_json

mod = Blueprint('cards', __name__, url_prefix='/cards')


def gather_conjurations(card):
    conjurations = card.conjurations if card.conjurations else []
    for conjuration in conjurations:
        conjurations = conjurations + gather_conjurations(conjuration)
    return conjurations


@mod.route('/')
def index():
    """Card gallery"""
    return render_template('cards/index.html', **global_json())


@mod.route('/<stub>/')
def detail(stub):
    """Card details"""
    card = Card.query.options(
        db.joinedload('conjurations')
    ).filter(Card.stub == stub).first()
    if not card:
        abort(404)
    # Gather up all related conjurations
    root_card = card if not card.summon_id else None
    if card.summon_id:
        summon_card = Card.query.get(card.summon_id)
        while summon_card:
            if not summon_card.summon_id:
                root_card = summon_card
                break
            summon_card = Card.query.get(summon_card.summon_id)
    conjurations = gather_conjurations(root_card) if root_card.conjurations else []
    # Gather stats
    if root_card.card_type == 'Phoenixborn':
        query = db.session.query(
            db.func.count(Deck.id).label('decks'),
            db.func.count(db.func.distinct(Deck.user_id)).label('users')
        ).filter(
            Deck.phoenixborn_id == root_card.id
        )
    else:
        query = db.session.query(
            db.func.count(DeckCard.deck_id).label('decks'),
            db.func.count(db.func.distinct(Deck.user_id)).label('users')
        ).join(
            Deck, Deck.id == DeckCard.deck_id
        ).filter(
            DeckCard.card_id == root_card.id
        )
    counts = query.filter(
        Deck.is_snapshot.is_(False)
    ).first()
    dice = Card.flags_to_dice(card.dice_flags)
    dice.remove('basic')
    return render_template(
        'cards/detail.html',
        card=json.loads(card.json),
        root_card=root_card,
        conjurations=conjurations,
        dice=dice,
        release=current_app.config['RELEASE_NAMES'][card.release],
        decks_count=counts.decks,
        users_count=counts.users
    )
