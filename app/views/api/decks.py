from flask import abort, Blueprint, flash, jsonify, request, url_for
from flask_login import current_user, login_required

from app import db
from app.exceptions import ApiError
from app.models.ashes_500 import Ashes500Revision, Ashes500Value
from app.models.card import Card, DiceFlags
from app.models.deck import Deck, DeckCard, DeckDie, DeckSelectedCard
from app.models.stream import Streamable
from app.jinja_globals import deck_title as compose_deck_title
from app.utils.stream import new_entity, refresh_entity, update_subscription

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
    source_entity_id = None
    if deck_id:
        deck = Deck.query.options(
            db.joinedload('cards'),
            db.joinedload('dice'),
            db.joinedload('selected_cards')
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
        deck.ashes_500_revision_id = data.get('ashes_500_revision')
    else:
        source_id = data.get('source_id')
        # Verify that the source_id is a legal source
        if source_id:
            source = db.session.query(Deck.entity_id).filter(
                Deck.id == source_id,
                Deck.is_snapshot.is_(not is_snapshot),
                db.or_(
                    Deck.user_id == current_user.id,
                    Deck.is_public.is_(True)
                )
            ).first()
            if not source:
                abort(404)
            source_entity_id = source.entity_id
        deck = Deck(
            entity_id=new_entity(),
            title=deck_title,
            description=data.get('description'),
            user_id=current_user.id,
            phoenixborn_id=data.get('phoenixborn'),
            is_snapshot=is_snapshot,
            is_public=is_public,
            source_id=source_id,
            ashes_500_revision_id=data.get('ashes_500_revision')
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
    card_counts = {int(key): int(value) for key, value in data.get('cards', {}).items()}
    # No idea how, but a Phoenixborn managed to get saved in a deck; so let's quash that possibility
    phoenixborn_ids = [
        x.id for x in db.session.query(Card.id).filter(Card.card_type == 'Phoenixborn').all()
    ]
    for card_id, count in card_counts.items():
        count = count if count <= 3 else 3
        if card_id in phoenixborn_ids:
            return jsonify({
                'error': (
                    'Your deck includes a Phoenixborn within the decklist (this should be '
                    'impossible; that it happened means a bug has occurred). Please remove the '
                    'offending card, or reload the page and try saving again. If you remember how '
                    'you added the Phoenixborn to the decklist, please '
                    '<a href="{}" class="error" target="_blank">contact me</a>.'
                ).format(url_for('home.feedback'))
            })
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
    
    # If this is an Ashes500 deck, calculate the deck's score
    if deck.ashes_500_revision_id:
        card_counts[deck.phoenixborn_id] = 1
        ashes_500_values = db.session.query(Ashes500Value).filter(
            Ashes500Value.revision_id == deck.ashes_500_revision_id,
            Ashes500Value.card_id.in_(card_counts.keys())
        )
        if not ashes_500_values:
            return jsonify({
                'error': (
                    'Unable to locate Ashes 500 revision. '
                    'Please disable Ashes 500, save the deck again, reload the page, '
                    'and re-enable Ashes 500 scoring to proceed.'
                )
            })
        deck_cost = 0
        for cost in ashes_500_values:
            card_cost = 0
            count = card_counts[cost.card_id]
            if cost.combo_card_id and cost.combo_card_id in card_counts:
                card_cost += cost.qty_1
                if count >= 2 and cost.qty_2:
                    card_cost += cost.qty_2
                if count == 3 and cost.qty_3:
                    card_cost += cost.qty_3
            elif not cost.combo_card_id:
                card_cost += cost.qty_1
                if count >= 2 and cost.qty_2:
                    card_cost += cost.qty_2
                if count == 3 and cost.qty_3:
                    card_cost += cost.qty_3
            deck_cost += card_cost
        deck.ashes_500_score = deck_cost
    else:
        deck.ashes_500_score = None

    # Finally save everything up!
    deck.selected_cards = []
    db.session.add(deck)
    if deck.is_public and deck.is_snapshot and source_entity_id:
        refresh_entity(deck.entity_id, 'deck', source_entity_id)
        update_subscription(source_entity_id, deck.entity_id)
    db.session.commit()
    # And finally set selected cards (first five, paid effects, and tutored cards; used for stats)
    # This happens after clearing them out because SQLAlchemy cannot handle the three way composite
    # index (tries to insert duplicates instead of updating intelligently based on tutor_card_id)
    first_five = frozenset(data.get('first_five', []))
    paid_effects = frozenset(data.get('effect_costs', []))
    tutor_map = data.get('tutor_map', {})
    selected_cards = []
    for card_id in paid_effects:
        if card_id not in first_five:
            selected_cards.append(DeckSelectedCard(
                card_id=card_id,
                is_paid_effect=True
            ))
    for card_id in first_five:
        selected_cards.append(DeckSelectedCard(
            card_id=card_id,
            is_first_five=True,
            is_paid_effect=card_id in paid_effects
        ))
    for tutor_id, card_id in tutor_map.items():
        selected_cards.append(DeckSelectedCard(
            card_id=card_id,
            tutor_card_id=tutor_id
        ))
    deck.selected_cards = selected_cards
    db.session.commit()

    return jsonify({'success': '{} successfully saved!'.format(
        'Snapshot' if is_snapshot else 'Deck'
    ), 'data': {
        'id': deck.id,
        'ashes_500_score': deck.ashes_500_score,
        'ashes_500_revision_id': deck.ashes_500_revision_id
    }})


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
