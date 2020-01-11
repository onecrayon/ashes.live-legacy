"""Deck-building and viewing public decks"""

import json

from flask import abort, Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm.session import make_transient

from app import db
from app.exceptions import Redirect
from app.models.card import Card, DiceFlags
from app.models.deck import Deck, DeckCard, DeckDie
from app.utils.ashes_500 import latest_ashes_500_revision
from app.utils.cards import gather_root_summons
from app.utils.comments import process_comments
from app.utils.decks import get_decks, get_decks_query, process_deck
from app.utils.releases import get_release_list
from app.utils.stream import new_entity, toggle_subscription
from app.views.forms.deck import SnapshotForm

mod = Blueprint('decks', __name__, url_prefix='/decks')


def get_deck_filters():
    phoenixborn = db.session.query(Card.name, Card.stub, Card.id).filter(
        Card.card_type == 'Phoenixborn'
    ).order_by(Card.name.asc()).all()
    filters = {
        's': request.args.get('s'),
        'phoenixborn': request.args.get('phoenixborn'),
        'card': request.args.get('card')
    }
    active_filters = []
    if filters['s']:
        active_filters.append(Deck.title.like('%' + filters['s'].replace('%', r'\%') + '%'))
    if filters['phoenixborn']:
        phoenixborn_id = next(
            (x.id for x in phoenixborn if x.stub == filters['phoenixborn']), None
        )
        if phoenixborn_id:
            active_filters.append(Deck.phoenixborn_id == phoenixborn_id)
        else:
            flash('Unable to find Phoenixborn; showing all decks.', 'error')
    filter_card = None
    if filters['card']:
        root_ids = []
        filter_card = Card.query.options(
            db.joinedload('summons')
        ).filter(Card.stub == filters['card']).first()
        root_ids = [x.id for x in gather_root_summons(filter_card)]
        active_filters.append(DeckCard.card_id.in_(root_ids))
    return filters, active_filters, phoenixborn, filter_card


@mod.route('/')
@mod.route('/<int:page>/')
def index(page=None):
    """View list of all public decks"""
    filters, active_filters, phoenixborn, filter_card = get_deck_filters()
    decks, card_map, page, pagination = get_decks(
        page, order_by='created', most_recent_public=True,
        filter_by_card=True if filter_card else False,
        filters=(active_filters or None)
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
        precon_decks=precon_decks,
        filters={k: v for k, v in filters.items() if v},
        filter_card=filter_card,
        phoenixborn=phoenixborn,
        latest_ashes_500=latest_ashes_500_revision(),
    )


@mod.route('/view/<int:deck_id>/', methods=['GET', 'POST'])
@mod.route('/view/<int:deck_id>/<int:page>/', methods=['GET', 'POST'])
def view(deck_id, page=1, show_saved=False):
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
    not_own_deck = (not current_user.is_authenticated or deck.user_id != current_user.id)
    if deck.is_snapshot and not deck.is_public and not_own_deck:
        abort(404)
    # Re-route to the latest public snapshot, if viewing a deck
    if not deck.is_snapshot and (not_own_deck or not show_saved):
        deck = deck.published_snapshot(full=True)
        if not deck:
            abort(404)
    sections = process_deck(deck)
    # Gather the releases required by this deck
    release_ids = set()
    for section in sections:
        for card in section['cards']:
            release_ids.add(card['release']['id'])
    release_ids.add(deck.phoenixborn.release_id)
    # Even if cards don't require a particular set, check for dice
    dice_to_release = {
        'ceremonial': 0,
        'charm': 0,
        'illusion': 0,
        'natural': 0,
        'divine': 6,
        'sympathy': 7,
        'time': 0,
    }
    for die in deck.dice:
        release_ids.add(dice_to_release[DiceFlags(die.die_flag).name])
    release_results = db.session.query(
        Deck.source_id, Deck.title, Deck.preconstructed_release
    ).filter(
        Deck.preconstructed_release.in_(list(release_ids))
    ).order_by(Deck.created.asc()).all()
    release_data = []
    for release in release_results:
        release_data.append({
            'preconstructed_id': release.source_id,
            'title': release.title
        })
        release_ids.remove(release.preconstructed_release)
    # Check to see if the core set remains; if there's leftover releases we're currently
    # just ignoring them because ¯\_(ツ)_/¯
    release_ids = list(release_ids)
    release_ids.sort()
    if release_ids and release_ids[0] == 0:
        release_data.insert(0, {
            'preconstructed_id': None,
            'title': 'Core Set'
        })
        
    # Check for outdated Ashes 500
    if deck.ashes_500_revision_id:
        latest_ashes_500 = latest_ashes_500_revision()
    # Gather comments
    try:
        source_entity_id = deck.source.entity_id if deck.source else deck.entity_id
        comments, pagination, last_seen_entity_id, comment_form = process_comments(
            source_entity_id, source_type='deck', source_version=deck.id, page=page,
            allow_commenting=deck.is_public, fallback_last_seen_entity_id=deck.entity_id
        )
    except Redirect as error:
        return redirect(error.url, code=error.status_code)
    return render_template(
        'decks/view.html',
        deck=deck,
        phoenixborn_stats=json.loads(deck.phoenixborn.json),
        sections=sections,
        releases=release_data,
        has_history=deck.has_snapshots,
        is_base_deck=show_saved,
        is_outdated=(deck.ashes_500_revision_id and deck.ashes_500_revision_id != latest_ashes_500),
        # Standard comment properties
        comment_version=deck.id,
        comments=comments,
        comment_last_seen=last_seen_entity_id,
        pagination_options={
            'view_path': 'decks.view' if not show_saved else 'decks.view_saved',
            'pages': pagination,
            'deck_id': deck_id,
            'page': page
        },
        comment_form=comment_form
    )


@mod.route('/view/<int:deck_id>/saved/')
@mod.route('/view/<int:deck_id>/saved/<int:page>/')
@login_required
def view_saved(deck_id, page=1):
    deck = Deck.query.get_or_404(deck_id)
    if deck.is_snapshot:
        return redirect(url_for('decks.view', deck_id=deck_id))
    return view(deck_id, page=page, show_saved=True)


@mod.route('/view/<int:deck_id>/subscribe/')
@login_required
def subscribe(deck_id):
    """Toggle subscription for this deck"""
    deck = Deck.query.get_or_404(deck_id)
    if deck.is_snapshot:
        deck = db.session.query(Deck).filter(Deck.id == deck.source_id).first()
    if not deck:
        abort(404)
    snapshot = deck.published_snapshot()
    toggle_subscription(deck.entity_id, fallback_last_seen=snapshot.entity_id if snapshot else None)
    return redirect(url_for('decks.view', deck_id=deck_id), code=303)


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
        form=form,
        latest_ashes_500=latest_ashes_500_revision()
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
    if source.is_snapshot:
        return redirect(url_for('decks.history', deck_id=source.source_id))
    filters = [
        Deck.is_snapshot.is_(True)
    ]
    if not own_deck:
        filters.append(Deck.source_id == source.id)
        filters.append(Deck.is_public.is_(True))
    else:
        filters.append(Deck.source_id == source.id)
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
        latest_ashes_500=latest_ashes_500_revision(),
        page=page,
        pages=pagination
    )


@mod.route('/mine/')
@mod.route('/mine/<int:page>/')
@login_required
def mine(page=None):
    """View logged-in player's decks"""
    filters, active_filters, phoenixborn, filter_card = get_deck_filters()
    active_filters = [
        Deck.user_id == current_user.id,
        Deck.is_snapshot.is_(False)
    ] + active_filters
    decks, card_map, page, pagination = get_decks(
        page, filters=active_filters,
        filter_by_card=True if filter_card else False
    )
    return render_template(
        'decks/mine.html',
        decks=decks,
        card_map=card_map,
        filters={k: v for k, v in filters.items() if v},
        filter_card=filter_card,
        phoenixborn=phoenixborn,
        latest_ashes_500=latest_ashes_500_revision(),
        page=page,
        pages=pagination
    )


@mod.route('/build/')
@mod.route('/build/<int:deck_id>/')
def build(deck_id=None):
    """Edit a deck"""
    deck = None if not deck_id else Deck.query.options(
        db.joinedload('cards'),
        db.joinedload('dice'),
        db.joinedload('phoenixborn'),
        db.joinedload('selected_cards')
    ).get(deck_id)
    if deck_id and not deck:
        abort(404)
    if not deck_id and not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    if deck_id:
        if not current_user.is_authenticated or deck.user_id != current_user.id:
            # User doesn't own this deck; redirect if we have a public snapshot
            # because this was probably an accidentally shared build link
            if deck.has_snapshots:
                return redirect(url_for('decks.view', deck_id=(
                    deck.id if not deck.is_snapshot else deck.source_id
                )))
            else:
                abort(404)
        elif deck.is_snapshot:
            return redirect(url_for('decks.build', deck_id=deck.source_id))
    deck_json = None
    if deck:
        if not current_user.is_authenticated or deck.user_id != current_user.id:
            abort(404)
        first_five = []
        effect_costs = []
        tutor_map = {}
        for selected_card in deck.selected_cards:
            if selected_card.is_first_five:
                first_five.append(selected_card.card_id)
            if selected_card.is_paid_effect:
                effect_costs.append(selected_card.card_id)
            if selected_card.tutor_card_id:
                tutor_map[selected_card.tutor_card_id] = selected_card.card_id
        deck_json = json.dumps({
            'id': deck.id,
            'title': deck.title,
            'description': deck.description,
            'phoenixborn': deck.phoenixborn_id,
            '_phoenixborn_data': {
                'name': deck.phoenixborn.name,
                'release': deck.phoenixborn.release_id
            },
            'dice': {DiceFlags(x.die_flag).name: x.count for x in deck.dice},
            'cards': {x.card_id: x.count for x in deck.cards},
            'first_five': first_five,
            'effect_costs': effect_costs,
            'tutor_map': tutor_map,
            'ashes_500_score': deck.ashes_500_score,
            'ashes_500_revision_id': deck.ashes_500_revision_id
        })
    user_release_ids_json = None
    if current_user.collection:
        user_release_ids_json = json.dumps([x.release_id for x in current_user.collection])
    return render_template(
        'decks/build.html',
        deck_json=deck_json,
        user_release_ids_json=user_release_ids_json,
        release_list_json=json.dumps(get_release_list())
    )


@mod.route('/clone/<int:deck_id>/')
@login_required
def clone(deck_id):
    # Simple check if the snapshot exists first (no joinedloads)
    deck = db.session.query(Deck.id).filter(
        Deck.is_snapshot.is_(True),
        Deck.id == deck_id
    ).first()
    if not deck:
        abort(404)
    # Then we grab a new entity_id first because it causes a commit and kills the process otherwise
    entity_id = new_entity()
    # Then we can finally grab our full deck and copy it
    deck = Deck.query.options(
        db.joinedload('cards'),
        db.joinedload('dice'),
        db.joinedload('selected_cards')
    ).filter(
        Deck.is_snapshot.is_(True),
        Deck.id == deck_id
    ).first()
    # Reset our deck object in order to clone it
    make_transient(deck)
    deck.id = None
    deck.entity_id = entity_id
    deck.title = 'Copy of {}'.format(deck.title)
    deck.user_id = current_user.id
    deck.is_snapshot = False
    deck.is_public = False
    deck.source_id = deck_id
    deck.created = None
    deck.modified = None
    deck.is_preconstructed = False
    deck.preconstructed_release = None
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
    selected_cards = []
    for card in deck.selected_cards:
        make_transient(card)
        card.deck_id = None
        selected_cards.append(card)
    deck.selected_cards = selected_cards
    db.session.add(deck)
    db.session.commit()
    return redirect(url_for('decks.build', deck_id=deck.id), code=303)
