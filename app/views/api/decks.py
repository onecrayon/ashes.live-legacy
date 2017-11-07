from flask import abort, current_app, Blueprint, flash, jsonify, request
from flask_login import current_user, login_required

from app import db
from app.models.card import DiceFlags
from app.models.deck import Deck, DeckCard, DeckDie
from app.template_filters import deck_title as compose_deck_title

mod = Blueprint('api_decks', __name__, url_prefix='/api/decks')


@mod.route('/')
def listing():
    return jsonify({'error': 'Coming soon'})


@mod.route('/', methods=['POST'])
@mod.route('/<int:deck_id>', methods=['POST'])
@mod.route('/snapshot', methods=['POST'], defaults={'is_snapshot': True})
@mod.route('/snapshot/<int:deck_id>', methods=['POST'], defaults={'is_snapshot': True})
@login_required
def save(deck_id=None, is_snapshot=False):
    data = request.get_json()

    # Do some validation
    deck_title = data.get('title')
    if deck_title and len(deck_title) > 255:
        return jsonify({'error': 'Deck does not validate.', 'validation': {
            'title': 'Title must be less than 255 characters long.'
        }})

    # Update or save deck data
    is_public = data.get('is_public', False)
    if deck_id:
        query = Deck.query
        if not is_snapshot:
           query = query.options(
                db.joinedload('cards'),
                db.joinedload('dice')
            )
        deck = query.get(deck_id)
        if (not deck or not current_user.is_authenticated or
                deck.user_id != current_user.id):
            abort(404)
        deck.title = deck_title
        deck.description = data.get('description')
        if is_snapshot:
            db.session.commit()
            return jsonify({'success': 'Snapshot successfully saved!'})
        deck.phoenixborn_id = data.get('phoenixborn')
    else:
        source_id = data.get('source_id')
        # Verify that the source_id is a legal source
        if source_id:
            source = db.session.query(Deck.id).filter(
                Deck.id == source_id,
                Deck.is_snapshot.is_(not is_snapshot),
                db.or_(
                    Deck.user_id == current_user.id,
                    Deck.is_public.is_(True)
                )
            ).first()
            if not source:
                abort(404)
        deck = Deck(
            title=deck_title,
            description=data.get('description'),
            user_id=current_user.id,
            phoenixborn_id=data.get('phoenixborn'),
            is_snapshot=is_snapshot,
            is_public=is_public,
            source_id=source_id
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

    return jsonify({'success': '{} successfully saved!'.format(
        'Snapshot' if is_snapshot else 'Deck'
    ), 'data': {'id': deck.id}})


@mod.route('/<int:deck_id>', methods=['DELETE'])
@login_required
def delete(deck_id):
    deck = Deck.query.options(db.joinedload('phoenixborn')).get(deck_id)
    if (not deck or not current_user.is_authenticated or
            deck.user_id != current_user.id):
        abort(404)
    title = compose_deck_title(deck)
    db.session.delete(deck)
    db.session.commit()
    success_message = 'Your deck "{}" has been deleted!'.format(title)
    flash(success_message, 'success')
    return jsonify({'success': success_message})
