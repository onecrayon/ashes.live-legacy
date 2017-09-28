from flask import current_app, Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import db
from app.models.card import DiceFlags
from app.models.deck import Deck, DeckCard, DeckDie

mod = Blueprint('api_decks', __name__, url_prefix='/api/decks')


@mod.route('/')
def listing():
    return jsonify({'error': 'Coming soon'})


@mod.route('/', methods=['POST'])
@mod.route('/<int:deck_id>', methods=['POST'])
@login_required
def save(deck_id=None):
    data = request.get_json()

    # Do some validation
    deck_title = data.get('title')
    if deck_title and len(deck_title) > 255:
        return jsonify({'error': 'Deck does not validate.', 'validation': {
            'title': 'Title must be less than 255 characters long.'
        }})

    # Update or save deck data
    if deck_id:
        deck = Deck.query.options(
            db.joinedload('cards'),
            db.joinedload('dice')
        ).get(deck_id)
        if not deck or deck.user_id != current_user.id:
            abort(404)
        deck.title = deck_title
        deck.description = data.get('description')
        deck.phoenixborn_id = data.get('phoenixborn')
    else:
        deck = Deck(
            title=deck_title,
            description=data.get('description'),
            user_id=current_user.id,
            phoenixborn_id=data.get('phoenixborn')
        )
    
    # Update the dice listing
    dice = []
    total_dice = 0
    for die, count in data.get('dice', {}).items():
        if count:
            if total_dice + count > 10:
                count = 10 - total_dice
            if count == 0:
                break
            total_dice = total_dice + count
            dice.append(DeckDie(
                die_flag=DiceFlags[die].value,
                count=count
            ))
    deck.dice = dice
    # And then the card listing
    deck.cards = [DeckCard(
        card_id=int(card_id),
        count=count if count <= 3 else 3
    ) for card_id, count in data.get('cards', {}).items()]
    # Finally save everything up!
    db.session.add(deck)
    db.session.commit()

    return jsonify({'success': 'Deck saved!', 'data': {'id': deck.id}})
