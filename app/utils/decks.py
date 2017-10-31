from collections import defaultdict
import math
from operator import itemgetter

from flask import current_app

from app import db
from app.models.deck import Deck


CardTypeOrdering = {
    'Ready Spells': 0,
    'Allies': 1,
    'Alteration Spells': 2,
    'Action Spells': 3,
    'Reaction Spells': 4,
    'Conjuration Deck': 5
}


def process_cards(card_map, deck_id, deck_cards):
    """Maps multiple decks worth of cards into a single dict"""
    for deck_card in deck_cards:
        card = deck_card.card if hasattr(deck_card, 'card') else deck_card
        card_id = card.card_id if hasattr(card, 'card_id') else card.id
        count = deck_card.count if hasattr(deck_card, 'count') else card.copies
        card_type = card.card_type
        if card_type.startswith('Conjur'):
            card_type = 'Conjuration Deck'
        elif card_type.endswith('y'):
            card_type = card_type[:-1] + 'ies'
        else:
            card_type = card_type + 's'
        card_map[deck_id].append({
            'id':card_id,
            'count': count,
            'name': card.name,
            'stub': card.stub,
            'type': card_type
        })
        if card.conjurations:
            process_cards(card_map, deck_id, card.conjurations)


def get_decks(filters, page, order_by='modified'):
    """Returns a generic query for grabbing decks and related data"""
    if not page:
        page = 1
    per_page = current_app.config['DEFAULT_PAGED_RESULTS']
    query = Deck.query.filter(filters).options(
        db.joinedload('phoenixborn').joinedload('conjurations'),
        db.joinedload('cards').joinedload('card').joinedload('conjurations'),
        db.joinedload('dice')
    ).order_by(getattr(Deck, order_by).desc()).limit(per_page).offset(
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
            key=lambda x: CardTypeOrdering[x['type']]
        )
    total_pages = math.ceil(query.limit(None).offset(None).count() / per_page)
    if total_pages > 1:
        pagination = list(range(1, total_pages + 1))
        spread = 2
        extra_right = spread - page + 1 if page - 1 < spread else 0
        extra_left = page + spread - total_pages if page + spread > total_pages else 0
        if page + spread + extra_right < total_pages - 2:
            del pagination[page + spread + extra_right:total_pages - 1]
        if page - spread - extra_left > 3:
            del pagination[1:page - spread - extra_left - 1]
    else:
        pagination = None
    return decks, card_map, page, pagination
