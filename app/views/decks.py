"""Deck-building and viewing public decks"""

import json

from flask import abort, Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm.session import make_transient

from app import db
from app.models.card import DiceFlags
from app.models.deck import Deck, DeckCard, DeckDie
from app.utils.cards import global_json
from app.utils.decks import get_decks, get_decks_query, process_deck
from app.views.forms.deck import SnapshotForm

mod = Blueprint('decks', __name__, url_prefix='/decks')


@mod.route('/')
@mod.route('/<int:page>/')
def index(page=None):
    """View list of all public decks"""
    decks, card_map, page, pagination = get_decks(
        page, order_by='created', most_recent_public=True
    )
    precon_decks = get_decks_query(filters=[
        Deck.is_preconstructed.is_(True)
    ], options=[
        db.joinedload('phoenixborn')
    ], most_recent_public=True).order_by(Deck.created.asc()).all()
    return render_template(
        'decks/index.html',
        decks=decks,
        card_map=card_map,
        page=page,
        pages=pagination,
        precon_decks=precon_decks
    )


@mod.route('/view/<int:deck_id>/')
def view(deck_id):
    """View a snapshot.
    
    If deck_id points to a deck, shows first public snapshot.
    """
    deck = Deck.query.options(
        db.joinedload('phoenixborn').joinedload('conjurations'),
        db.joinedload('cards').joinedload('card').joinedload('conjurations'),
        db.joinedload('dice'),
        db.joinedload('user'),
        db.joinedload('source').joinedload('phoenixborn')
    ).get_or_404(deck_id)
    if deck.is_snapshot and not deck.is_public and (not current_user.is_authenticated or
            deck.user_id != current_user.id):
        abort(404)
    # Re-route to the latest public snapshot, if viewing a deck
    if not deck.is_snapshot:
        deck = deck.published_snapshot(full=True)
        if not deck:
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
    deck = Deck.query.options(
        db.joinedload('phoenixborn').joinedload('conjurations'),
        db.joinedload('cards').joinedload('card').joinedload('conjurations'),
        db.joinedload('dice')
    ).get_or_404(deck_id)
    if not current_user.is_authenticated or deck.user_id != current_user.id:
        abort(404)
    if not deck.is_snapshot:
        return redirect(url_for('decks.build', deck_id=deck_id))
    form = SnapshotForm(obj=deck)
    if form.validate_on_submit():
        # Save changes to snapshot
        deck.title = form.title.data
        deck.description = form.description.data
        db.session.commit()
        flash('Snapshot updated!', 'success')
    return render_template(
        'decks/edit.html',
        deck=deck,
        card_map={deck.id: process_deck(deck)},
        form=form
    )


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
    published_deck = source.published_snapshot()
    if not published_deck and not own_deck:
        abort(404)
    shared_id = source.source_id if source.is_snapshot else source.id
    filters = [
        Deck.is_snapshot.is_(True)
    ]
    if not own_deck:
        filters.append(Deck.source_id == shared_id)
        filters.append(Deck.is_public.is_(True))
    else:
        filters.append(Deck.source_id == shared_id)
    decks, card_map, page, pagination = get_decks(
        page, filters=filters, order_by='created'
    )
    card_map[source.id] = process_deck(source)
    return render_template(
        'decks/history.html',
        deck=source if own_deck else decks[0],
        published_deck=source if own_deck else published_deck,
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
    decks, card_map, page, pagination = get_decks(page, filters=[
        Deck.user_id == current_user.id,
        Deck.is_snapshot.is_(False)
    ])
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
    if deck_id and deck.is_snapshot:
        return redirect(url_for('decks.build', deck_id=deck.source_id))
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


@mod.route('/clone/<int:deck_id>/')
@login_required
def clone(deck_id):
    deck = Deck.query.options(
        db.joinedload('cards'),
        db.joinedload('dice')
    ).filter(
        Deck.is_snapshot.is_(True),
        Deck.id == deck_id
    ).first()
    if not deck:
        abort(404)
    # Reset our deck object in order to clone it
    make_transient(deck)
    deck.id = None
    deck.title = 'Copy of {}'.format(deck.title)
    deck.user_id = current_user.id
    deck.is_snapshot = False
    deck.is_public = False
    deck.source_id = deck_id
    deck.created = None
    dice = []
    for die in deck.dice:
        make_transient(die)
        die.deck_id = None
        dice.append(die)
    deck.dice = dice
    cards = []
    for card in deck.cards:
        make_transient(card)
        card.deck_id = None
        cards.append(card)
    deck.cards = cards
    db.session.add(deck)
    db.session.commit()
    return redirect(url_for('decks.build', deck_id=deck.id), code=303)
