"""Deck-building and viewing public decks"""

import json

from flask import abort, Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.models.card import DiceFlags
from app.models.deck import Deck
from app.utils.cards import global_json
from app.utils.decks import get_decks, process_deck

mod = Blueprint('decks', __name__, url_prefix='/decks')


@mod.route('/')
@mod.route('/<int:page>/')
def index(page=None):
    """View list of all public decks"""
    decks, card_map, page, pagination = get_decks(db.and_(
        Deck.is_snapshot.is_(True),
        Deck.is_public.is_(True)
    ), page, order_by='created', most_recent_public=True)
    return render_template(
        'decks/index.html',
        decks=decks,
        card_map=card_map,
        page=page,
        pages=pagination
    )


@mod.route('/view/<int:deck_id>/')
def view(deck_id):
    """View a public deck"""
    deck = Deck.query.options(
        db.joinedload('phoenixborn').joinedload('conjurations'),
        db.joinedload('cards').joinedload('card').joinedload('conjurations'),
        db.joinedload('dice'),
        db.joinedload('user'),
        db.joinedload('source').joinedload('phoenixborn')
    ).get_or_404(deck_id)
    if not deck.is_public and (not current_user.is_authenticated or
            deck.user_id != current_user.id):
        abort(404)
    return render_template(
        'decks/view.html',
        deck=deck,
        sections=process_deck(deck),
        has_history=deck.has_snapshots
    )


@mod.route('/edit/<int:deck_id>/', methods=['GET', 'POST'])
def edit(deck_id):
    """Edit a deck snapshot (redirects for actual decks)"""
    deck = Deck.query.get_or_404(deck_id)
    if not current_user.is_authenticated or deck.user_id != current_user.id:
        abort(404)
    if not deck.is_snapshot:
        redirect(url_for('deck.build', deck_id=deck_id))
    return render_template('wip.html')


@mod.route('/view/<int:deck_id>/history/')
@mod.route('/view/<int:deck_id>/history/<int:page>/')
def history(deck_id, page=None):
    """View the snapshots for public or own deck"""
    source = Deck.query.options(
        db.joinedload('phoenixborn').joinedload('conjurations'),
        db.joinedload('cards').joinedload('card').joinedload('conjurations'),
        db.joinedload('dice'),
        db.joinedload('user')
    ).get_or_404(deck_id)
    own_deck = (
        current_user.is_authenticated and source.user_id == current_user.id
    )
    if not source.public_snapshots(limit=1) and not own_deck:
        abort(404)
    if not own_deck:
        filters = db.and_(
            Deck.is_snapshot.is_(True),
            Deck.is_public.is_(True)
        )
    else:
        filters = db.and_(
            Deck.is_snapshot.is_(True)
        )
    decks, card_map, page, pagination = get_decks(filters, page, order_by='created')
    card_map[source.id] = process_deck(source)
    return render_template(
        'decks/history.html',
        deck=source if own_deck else decks[0],
        snapshots=decks,
        card_map=card_map,
        page=page,
        pages=pagination
    )


@mod.route('/mine/')
@mod.route('/mine/<int:page>/')
@login_required
def mine(page=None):
    """View logged-in player's decks"""
    decks, card_map, page, pagination = get_decks(db.and_(
        Deck.user_id == current_user.id,
        Deck.is_snapshot.is_(False)
    ), page)
    return render_template(
        'decks/mine.html',
        decks=decks,
        card_map=card_map,
        page=page,
        pages=pagination
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
        if not current_user.is_authenticated or deck.user_id != current_user.id:
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
