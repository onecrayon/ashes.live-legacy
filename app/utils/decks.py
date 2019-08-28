from collections import OrderedDict
from operator import itemgetter

from flask import current_app

from app import db
from app.models.deck import Deck, DeckCard
from app.utils import get_pagination


def get_release_mapping():
    releases = Release.query.all()
    return {x.id: x for x in releases}


def process_cards(section_map, deck_cards, release_mapping=None):
    """Maps a deck's cards into sections"""
    if not release_mapping:
        release_mapping = get_release_mapping()
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
        release = release_mapping.get(card.release_id)
        section_map[card_type].append({
            'id':card_id,
            'count': count,
            'name': card.name,
            'stub': card.stub,
            'type': card_type,
            'phoenixborn': card.phoenixborn,
            'release': {
                'id': release.id,
                'name': release.name
            }
        })
        if card.conjurations:
            process_cards(section_map, card.conjurations, release_mapping=release_mapping)


def process_deck(deck, release_mapping=None):
    section_map = OrderedDict([
        ('Ready Spells', []),
        ('Allies', []),
        ('Alteration Spells', []),
        ('Action Spells', []),
        ('Reaction Spells', []),
        ('Conjuration Deck', [])
    ])
    if not release_mapping:
        release_mapping = get_release_mapping()
    process_cards(section_map, deck.cards, release_mapping=release_mapping)
    if deck.phoenixborn.conjurations:
        process_cards(section_map, deck.phoenixborn.conjurations, release_mapping=release_mapping)
    sections = []
    for section, cards in section_map.items():
        if not cards:
            continue
        # Ensure there are no duplicate conjurations
        if section == 'Conjuration Deck':
            conjuration_ids = set()
            unique_cards = []
            for card in cards:
                if card['id'] not in conjuration_ids:
                    conjuration_ids.add(card['id'])
                    unique_cards.append(card)
            cards = unique_cards
        sections.append({
            'heading': section,
            'count': sum(x['count'] for x in cards),
            'cards': sorted(cards, key=itemgetter('name'))
        })
    return sections


def get_decks_query(filters=None, options=None, most_recent_public=False):
    """Returns a generic query for grabbing decks and related data"""
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
            db.or_(
                Deck.created < deck_comp.created,
                db.and_(
                    Deck.created == deck_comp.created,
                    Deck.id < deck_comp.id
                )
            )
        )).filter(
            deck_comp.id.is_(None),
            Deck.is_snapshot.is_(True),
            Deck.is_public.is_(True)
        )
    return query


def get_decks(page=None, filters=None, order_by='modified', most_recent_public=False,
              filter_by_card=False):
    """Returns a list of decks, their card mapping, and pagination info"""
    if not page:
        page = 1
    per_page = current_app.config['DEFAULT_PAGED_RESULTS']
    # FIXME: figure out a more performant method to load this data
    query = get_decks_query(filters=filters, options=[
        db.joinedload('phoenixborn').joinedload('conjurations'),
        db.joinedload('cards').joinedload('card').joinedload('conjurations'),
        db.joinedload('dice'),
        db.joinedload('user')
    ], most_recent_public=most_recent_public)
    if filter_by_card:
        query = query.outerjoin(DeckCard, DeckCard.deck_id == Deck.id)
    decks = query.order_by(getattr(Deck, order_by).desc()).limit(per_page).offset(
        (page - 1) * per_page
    ).all()
    card_map = {}
    release_mapping = get_release_mapping()
    for deck in decks:
        card_map[deck.id] = process_deck(deck, release_mapping=release_mapping)
    pagination = get_pagination(query.count(), page, per_page)
    return decks, card_map, page, pagination
