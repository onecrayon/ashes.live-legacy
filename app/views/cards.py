"""Card gallery"""

import json

from flask import abort, current_app, Blueprint, url_for, redirect, render_template
from flask_login import login_required

from app import db
from app.exceptions import Redirect
from app.models.card import Card
from app.models.deck import Deck, DeckCard
from app.utils.comments import process_comments
from app.utils.stream import toggle_subscription

mod = Blueprint('cards', __name__, url_prefix='/cards')


def gather_conjurations(card):
    conjurations = card.conjurations if card.conjurations else []
    for conjuration in conjurations:
        conjurations = conjurations + gather_conjurations(conjuration)
    return conjurations


def gather_root_summons(card):
    if not card.summons:
        return [card]
    root_summons = []
    for summon in card.summons:
        root_summons = root_summons + gather_root_summons(summon)
    return root_summons


@mod.route('/')
def index():
    """Card gallery"""
    return render_template('cards/index.html')


@mod.route('/<stub>/', methods=['GET', 'POST'])
@mod.route('/<stub>/<int:page>/', methods=['GET', 'POST'])
def detail(stub, page=1):
    """Card details"""
    card = Card.query.options(
        db.joinedload('conjurations'),
        db.joinedload('summons')
    ).filter(Card.stub == stub).first()
    if not card:
        abort(404)
    # Gather up all related conjurations
    root_cards = gather_root_summons(card)
    conjurations = []
    phoenixborn_ids = []
    non_phoenixborn_ids = []
    for root_card in root_cards:
        if root_card.card_type == 'Phoenixborn':
            phoenixborn_ids.append(root_card.id)
        else:
            non_phoenixborn_ids.append(root_card.id)
        conjurations = conjurations + gather_conjurations(root_card)
    # Remove duplicate conjurations, if any
    conjuration_ids = set()
    unique_conjurations = []
    for conjuration in conjurations:
        if conjuration.id not in conjuration_ids:
            conjuration_ids.add(conjuration.id)
            unique_conjurations.append(conjuration)
    conjurations = unique_conjurations

    # Gather stats
    phoenixborn_counts = db.session.query(
        db.func.count(Deck.id).label('decks'),
        db.func.count(db.func.distinct(Deck.user_id)).label('users')
    ).filter(
        Deck.phoenixborn_id == root_card.id,
        Deck.is_snapshot.is_(False)
    ).first() if phoenixborn_ids else None
    card_counts = db.session.query(
        db.func.count(DeckCard.deck_id).label('decks'),
        db.func.count(db.func.distinct(Deck.user_id)).label('users')
    ).join(
        Deck, Deck.id == DeckCard.deck_id
    ).filter(
        DeckCard.card_id == root_card.id,
        Deck.is_snapshot.is_(False)
    ).first() if non_phoenixborn_ids else None
    counts = {
        'decks': 0,
        'users': 0
    }
    if phoenixborn_counts:
        counts['decks'] += phoenixborn_counts.decks
        counts['users'] += phoenixborn_counts.users
    if card_counts:
        counts['decks'] += card_counts.decks
        counts['users'] += card_counts.users
    dice = Card.flags_to_dice(card.dice_flags)
    dice.remove('basic')
    # Grab preconstructed deck, if available
    preconstructed = db.session.query(Deck.source_id, Deck.title).filter(
        db.or_(
            Deck.phoenixborn_id == card.id,
            Deck.title == current_app.config['RELEASE_NAMES'][card.release]
        ),
        Deck.is_snapshot.is_(True),
        Deck.is_public.is_(True),
        Deck.is_preconstructed.is_(True)
    ).first()
    # Grab Phoenixborn related card, if available
    phoenixborn_card = None
    if card.phoenixborn and card.card_type not in ('Conjuration', 'Conjured Alteration Spell'):
        phoenixborn_card = db.session.query(Card.stub, Card.name).filter(
            Card.name == card.phoenixborn,
            Card.card_type == 'Phoenixborn'
        ).first()
    elif card.card_type == 'Phoenixborn':
        phoenixborn_card = db.session.query(Card.stub, Card.name).filter(
            Card.phoenixborn == card.name,
            Card.card_type.notin_(('Conjuration', 'Conjured Alteration Spell'))
        ).first()
    # Gather comments
    try:
        comments, pagination, last_seen_entity_id, comment_form = process_comments(
            card.entity_id, source_type='card', source_version=card.version, page=page
        )
    except Redirect as error:
        return redirect(error.url, code=error.status_code)
    return render_template(
        'cards/detail.html',
        card=json.loads(card.json),
        root_cards=root_cards,
        conjurations=conjurations,
        dice=dice,
        release=current_app.config['RELEASE_NAMES'][card.release],
        decks_count=counts['decks'],
        users_count=counts['users'],
        preconstructed={
            'url': url_for('decks.view', deck_id=preconstructed.source_id),
            'title': preconstructed.title
        } if preconstructed else None,
        phoenixborn_card=phoenixborn_card,
        # Standard comment properties
        comment_version=card.version,
        comments=comments,
        comment_last_seen=last_seen_entity_id,
        pagination_options={
            'view_path': 'cards.detail',
            'pages': pagination,
            'stub': stub,
            'page': page
        },
        comment_form=comment_form
    )


@mod.route('/<stub>/subscribe/')
@login_required
def subscribe(stub):
    """Toggle subscription for this card"""
    card = db.session.query(Card.entity_id).filter(Card.stub == stub).first()
    if not card:
        abort(404)
    toggle_subscription(card.entity_id)
    return redirect(url_for('cards.detail', stub=stub), code=303)
