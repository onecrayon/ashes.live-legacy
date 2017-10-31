"""Deck-building and viewing public decks"""

import json

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app import db
from app.models.card import DiceFlags
from app.models.deck import Deck
from app.utils.cards import global_json
from app.utils.decks import get_decks

mod = Blueprint('decks', __name__, url_prefix='/decks')


@mod.route('/')
def index():
    """View list of all public decks"""
    return render_template('wip.html')


@mod.route('/<deck_stub>/')
def view(deck_id=None, deck_stub=None):
    """View a public deck"""
    return render_template('wip.html')


def render_snapshots(deck_id=None, deck_stub=None, page=None):
    """View the snapshots for public or own deck"""
    return render_template('wip.html')


@mod.route('/<int:deck_id>/snapshots/')
@mod.route('/<int:deck_id>/snapshots/<int:page>/')
@login_required
def my_snapshots(deck_id, page=None):
    return render_snapshots(deck_id=deck_id, page=page)


@mod.route('/<deck_stub>/snapshots/')
@mod.route('/<deck_stub>/snapshots/<int:page>/')
def snapshots(deck_stub, page=None):
    return render_snapshots(deck_stub=deck_stub, page=page)


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
