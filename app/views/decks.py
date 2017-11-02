"""Deck-building and viewing public decks"""

import json

from flask import abort, Blueprint, render_template
from flask_login import current_user, login_required

from app import db
from app.models.card import DiceFlags
from app.models.deck import Deck
from app.utils.cards import global_json
from app.utils.decks import get_decks, process_deck

mod = Blueprint('decks', __name__, url_prefix='/decks')


@mod.route('/')
def index():
    """View list of all public decks"""
    return render_template('wip.html')


@mod.route('/<int:deck_id>/')
def view(deck_id):
    """View a public deck"""
    return render_template('wip.html')


@mod.route('/<int:deck_id>/history/')
@mod.route('/<int:deck_id>/history/<int:page>/')
def snapshots(deck_id, page=None):
    """View the snapshots for public or own deck"""
    source = Deck.query.options(
        db.joinedload('phoenixborn').joinedload('conjurations'),
        db.joinedload('cards').joinedload('card').joinedload('conjurations'),
        db.joinedload('dice'),
        db.joinedload('user')
    ).get(deck_id)
    if not source:
        abort(404)
    own_deck = source.user_id == current_user.id
    if not source.public_snapshots(limit=1) and not own_deck:
        abort(404)
    if not own_deck:
        filters = db.and_(
            Deck.is_snapshot.is_(True),
            Deck.is_public.is_(True)
        )
    else:
        filters = db.and_(
            Deck.is_snapshot.is_(True)
        )
    decks, card_map, page, pagination = get_decks(filters, page, order_by='created')
    process_deck(source, card_map)
    return render_template(
        'decks/history.html',
        deck=source if own_deck else decks[0],
        snapshots=decks,
        card_map=card_map,
        page=page,
        pages=pagination
    )


@mod.route('/mine/')
@mod.route('/mine/<int:page>/')
@login_required
def mine(page=None):
    """View logged-in player's decks"""
    decks, card_map, page, pagination = get_decks(db.and_(
        Deck.user_id == current_user.id,
        Deck.is_snapshot.is_(False)
    ), page)
    return render_template(
        'decks/mine.html',
        decks=decks,
        card_map=card_map,
        page=page,
        pages=pagination
    )


@mod.route('/build/')
@mod.route('/build/<int:deck_id>/')
@login_required
def build(deck_id=None):
    """Edit a deck"""
    deck = None if not deck_id else Deck.query.options(
        db.joinedload('cards'),
        db.joinedload('dice')
    ).get(deck_id)
    if deck_id and not deck:
        abort(404)
    deck_json = None
    if deck:
        if deck.user_id != current_user.id:
            abort(404)
        deck_json = json.dumps({
            'id': deck.id,
            'title': deck.title,
            'description': deck.description,
            'phoenixborn': deck.phoenixborn_id,
            'dice': {DiceFlags(x.die_flag).name: x.count for x in deck.dice},
            'cards': {x.card_id: x.count for x in deck.cards}
        })
    return render_template('decks/build.html', deck_json=deck_json, **global_json())
