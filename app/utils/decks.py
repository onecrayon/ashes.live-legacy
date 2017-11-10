from collections import OrderedDict
import math
from operator import itemgetter

from flask import current_app

from app import db
from app.models.deck import Deck


def process_cards(section_map, deck_cards):
    """Maps a deck's cards into sections"""
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
        section_map[card_type].append({
            'id':card_id,
            'count': count,
            'name': card.name,
            'stub': card.stub,
            'type': card_type,
            'phoenixborn': card.phoenixborn
        })
        if card.conjurations:
            process_cards(section_map, card.conjurations)


def process_deck(deck):
    section_map = OrderedDict([
        ('Ready Spells', []),
        ('Allies', []),
        ('Alteration Spells', []),
        ('Action Spells', []),
        ('Reaction Spells', []),
        ('Conjuration Deck', [])
    ])
    process_cards(section_map, deck.cards)
    if deck.phoenixborn.conjurations:
        process_cards(section_map, deck.phoenixborn.conjurations)
    sections = []
    for section, cards in section_map.items():
        if not cards:
            continue
        sections.append({
            'heading': section,
            'count': sum(x['count'] for x in cards),
            'cards': sorted(cards, key=itemgetter('name'))
        })
    return sections


def get_decks_query(filters=None, options=None, most_recent_public=False):
    query = Deck.query
    if options:
        query = query.options(*options)
    if filters:
        query = query.filter(*filters)
    # Fetch the most recent public snapshot via the LEFT JOIN trick of comparing dates and
    # returning the only entry with a null value in the JOIN
    if most_recent_public:
        deck_comp = db.aliased(Deck)
        query = query.outerjoin(deck_comp, db.and_(
            Deck.source_id == deck_comp.source_id,
            deck_comp.is_snapshot.is_(True),
            deck_comp.is_public.is_(True),
            Deck.created < deck_comp.created
        )).filter(
            deck_comp.id.is_(None),
            Deck.is_snapshot.is_(True),
            Deck.is_public.is_(True)
        )
    return query


def get_decks(page, filters=None, order_by='modified', most_recent_public=False):
    """Returns a generic query for grabbing decks and related data"""
    if not page:
        page = 1
    per_page = current_app.config['DEFAULT_PAGED_RESULTS']
    query = get_decks_query(filters=filters, options=[
        db.joinedload('phoenixborn').joinedload('conjurations'),
        db.joinedload('cards').joinedload('card').joinedload('conjurations'),
        db.joinedload('dice'),
        db.joinedload('user')
    ], most_recent_public=most_recent_public).filter(*filters)
    decks = query.order_by(getattr(Deck, order_by).desc()).limit(per_page).offset(
        (page - 1) * per_page
    ).all()
    card_map = {}
    for deck in decks:
        card_map[deck.id] = process_deck(deck)
    total_pages = math.ceil(query.count() / per_page)
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
