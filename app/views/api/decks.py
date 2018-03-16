from flask import abort, Blueprint, flash, jsonify, request, url_for
from flask_login import current_user, login_required

from app import db
from app.exceptions import ApiError
from app.models.card import DiceFlags
from app.models.deck import Deck, DeckCard, DeckDie
from app.models.stream import Streamable
from app.template_filters import deck_title as compose_deck_title
from app.utils.stream import new_entity

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
        deck = Deck.query.options(
            db.joinedload('cards'),
            db.joinedload('dice')
        ).get(deck_id)
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
            entity_id=new_entity(),
            title=deck_title,
            description=data.get('description'),
            user_id=current_user.id,
            phoenixborn_id=data.get('phoenixborn'),
            is_snapshot=is_snapshot,
            is_public=is_public,
            source_id=source_id
        )

    # We only save a new snapshot if it differs from the previous one,
    # so grab the necessary data to compare the two
    has_changes = False
    previous = None
    previous_cards = {}
    previous_dice = {}
    if deck.is_snapshot:
        # Ensure that something differs from the previous snapshot
        previous_query = Deck.query.options(
            db.joinedload('cards'), db.joinedload('dice')
        ).filter(
            Deck.source_id == deck.source_id,
            Deck.is_snapshot.is_(True),
            Deck.user_id == current_user.id
        )
        if deck.is_public:
            previous_query = previous_query.filter(Deck.is_public.is_(True))
        previous = previous_query.order_by(Deck.created.desc()).first()
        if previous and previous.phoenixborn_id == deck.phoenixborn_id:
            previous_cards = {x.card_id: x.count for x in previous.cards}
            previous_dice = {
                DiceFlags(x.die_flag).name: x.count for x in previous.dice
            }
        else:
            has_changes = True

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
            prior = previous_dice.get(die)
            if not prior or prior != count:
                has_changes = True
    deck.dice = dice
    # And then the card listing
    cards = []
    for card_id, count in data.get('cards', {}).items():
        count = count if count <= 3 else 3
        card_id = int(card_id)
        cards.append(DeckCard(
            card_id=card_id,
            count=count
        ))
        prior = previous_cards.get(card_id)
        if not prior or prior != count:
            has_changes = True
    deck.cards = cards
    if previous and not has_changes:
        return jsonify({
            'error': (
                'Decklist and dice have not changed since your last snapshot. '
                '<a href="{}" class="error" target="_blank">Edit your previous '
                'snapshot\'s title &amp; description</a>.'
            ).format(url_for('decks.edit', deck_id=previous.id))
        })

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
    if not deck or deck.user_id != current_user.id:
        abort(404)
    # Check for public snapshots (public decks cannot be deleted)
    if deck.published_snapshot():
        raise ApiError('This deck has been published, and cannot be deleted.')
    entity_ids = []
    snapshots = db.session.query(Deck).filter(
        Deck.is_snapshot.is_(True),
        Deck.source_id == deck_id
    ).all()
    for snapshot in snapshots:
        has_derivatives = db.session.query(Deck.id).filter(
            Deck.source_id == snapshot.id
        ).count() > 0
        if has_derivatives:
            raise ApiError('This deck has been cloned, and cannot be deleted.')
        entity_ids.append(snapshot.entity_id)
        db.session.delete(snapshot)
    title = compose_deck_title(deck)
    entity_ids.append(deck.entity_id)
    db.session.query(Streamable).filter(
        Streamable.entity_id.in_(entity_ids)
    ).delete(synchronize_session=False)
    db.session.delete(deck)
    db.session.commit()
    success_message = 'Your deck "{}" has been deleted!'.format(title)
    flash(success_message, 'success')
    return jsonify({'success': success_message})
