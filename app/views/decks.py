"""Deck-building and viewing public decks"""

import json

from flask import current_app, Blueprint, render_template
from flask_login import current_user, login_required

from app import db
from app.models.card import DiceFlags
from app.models.deck import Deck
from app.services.cards import global_json

mod = Blueprint('decks', __name__, url_prefix='/decks')


@mod.route('/')
def index():
    """View list of all public decks"""
    return render_template('wip.html')


@mod.route('/<int:deck_id>/')
def view(deck_id):
    """View a public or own deck"""
    return render_template('wip.html')


@mod.route('/mine/')
@mod.route('/mine/<int:page>/')
@login_required
def mine(page=None):
    """View logged-in player's decks"""
    if not page:
        page = 1
    decks = Deck.query.options(
        db.joinedload('phoenixborn'),
        db.joinedload('cards'),
        db.joinedload('dice')
    ).filter(
        Deck.user_id == current_user.id
    ).order_by(Deck.modified.desc()).limit(
        current_app.config['DEFAULT_PAGED_RESULTS']
    ).offset((page - 1) * current_app.config['DEFAULT_PAGED_RESULTS']).all()
    # TODO: parse and order the card results
    return render_template('decks/mine.html', decks=decks)


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
