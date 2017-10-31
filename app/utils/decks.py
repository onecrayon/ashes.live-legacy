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
