"""Deck-building and viewing public decks"""

from collections import defaultdict
import json
import math
from operator import itemgetter

from flask import current_app, Blueprint, render_template
from flask_login import current_user, login_required

from app import db
from app.models.card import DiceFlags
from app.models.deck import Deck
from app.utils.cards import global_json
from app.utils.decks import process_cards, CardTypeOrdering

mod = Blueprint('decks', __name__, url_prefix='/decks')


@mod.route('/')
def index():
    """View list of all public decks"""
    return render_template('wip.html')


@mod.route('/<int:deck_id>/')
@mod.route('/<deck_stub>/')
def view(deck_id=None, deck_stub=None):
    """View a public or own deck"""
    return render_template('wip.html')


@mod.route('/<int:deck_id>/snapshots/')
@mod.route('/<int:deck_id>/snapshots/<int:page>/')
@mod.route('/<deck_stub>/snapshots/')
@mod.route('/<deck_stub>/snapshots/<int:page>/')
def snapshots(deck_id=None, deck_stub=None, page=None):
    """View the snapshots for public or own deck"""
    return render_template('wip.html')


@mod.route('/mine/')
@mod.route('/mine/<int:page>/')
@login_required
def mine(page=None):
    """View logged-in player's decks"""
    per_page = current_app.config['DEFAULT_PAGED_RESULTS']
    query = get_deck_query(page).filter(
        Deck.user_id == current_user.id,
        Deck.is_snapshot.is_(False)
    )
    decks = query.all()
    card_map = defaultdict(list)
    for deck in decks:
        process_cards(card_map, deck.id, deck.cards)
        if deck.phoenixborn.conjurations:
            process_cards(card_map, deck.id, deck.phoenixborn.conjurations)
        card_map[deck.id] = sorted(
            sorted(card_map[deck.id], key=itemgetter('name')),
            key=lambda x: CardTypeOrdering[x['type']]
        )
    total_pages = math.ceil(query.limit(None).offset(None).count() / per_page)
    if total_pages > 1:
        pages = list(range(1, total_pages + 1))
        spread = 2
        extra_right = spread - page + 1 if page - 1 < spread else 0
        extra_left = page + spread - total_pages if page + spread > total_pages else 0
        if page + spread + extra_right < total_pages - 2:
            del pages[page + spread + extra_right:total_pages - 1]
        if page - spread - extra_left > 3:
            del pages[1:page - spread - extra_left - 1]
    else:
        pages = None
    return render_template(
        'decks/mine.html',
        decks=decks,
        card_map=card_map,
        page=page,
        pages=pages
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
