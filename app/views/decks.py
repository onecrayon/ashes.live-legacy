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
from app.services.cards import global_json

mod = Blueprint('decks', __name__, url_prefix='/decks')


TypeOrdering = {
    'Ready Spell': 0,
    'Ally': 1,
    'Alteration Spell': 2,
    'Action Spell': 3,
    'Reaction Spell': 4,
    'Conjurations': 5
}


@mod.route('/')
def index():
    """View list of all public decks"""
    return render_template('wip.html')


@mod.route('/<int:deck_id>/')
def view(deck_id):
    """View a public or own deck"""
    return render_template('wip.html')


def process_cards(card_map, deck_id, deck_cards):
    for deck_card in deck_cards:
        card = deck_card.card if hasattr(deck_card, 'card') else deck_card
        card_id = card.card_id if hasattr(card, 'card_id') else card.id
        count = deck_card.count if hasattr(deck_card, 'count') else card.copies
        card_map[deck_id].append({
            'id':card_id,
            'count': count,
            'name': card.name,
            'stub': card.stub,
            'type': card.card_type if not card.card_type.startswith('Conjur')
                else 'Conjurations'
        })
        if card.conjurations:
            process_cards(card_map, deck_id, card.conjurations)


@mod.route('/mine/')
@mod.route('/mine/<int:page>/')
@login_required
def mine(page=None):
    """View logged-in player's decks"""
    if not page:
        page = 1
    per_page = current_app.config['DEFAULT_PAGED_RESULTS']
    query = Deck.query.options(
        db.joinedload('phoenixborn').joinedload('conjurations'),
        db.joinedload('cards').joinedload('card').joinedload('conjurations'),
        db.joinedload('dice')
    ).filter(
        Deck.user_id == current_user.id
    ).order_by(Deck.modified.desc()).limit(per_page).offset(
        (page - 1) * per_page
    )
    decks = query.all()
    card_map = defaultdict(list)
    for deck in decks:
        process_cards(card_map, deck.id, deck.cards)
        if deck.phoenixborn.conjurations:
            process_cards(card_map, deck.id, deck.phoenixborn.conjurations)
        card_map[deck.id] = sorted(
            sorted(card_map[deck.id], key=itemgetter('name')),
        key=lambda x: TypeOrdering[x['type']])
    total_pages = math.ceil(query.limit(None).offset(None).count() / per_page)
    pages = list(range(1, total_pages + 1))
    spread = 2
    extra_right = spread - page + 1 if page - 1 < spread else 0
    extra_left = page + spread - total_pages if page + spread > total_pages else 0
    if page + spread + extra_right < total_pages - 2:
        del pages[page + spread + extra_right:total_pages - 1]
    if page - spread - extra_left > 3:
        del pages[1:page - spread - extra_left - 1]
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
