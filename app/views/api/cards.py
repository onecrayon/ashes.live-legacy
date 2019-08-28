import json

from flask import Blueprint, jsonify, request
from flask_login import current_user
from sqlalchemy_fulltext import FullTextSearch
import sqlalchemy_fulltext.modes as FullTextMode

from app import db
from app.models.ashes_500 import Ashes500Revision
from app.models.card import Card, NameTextSearch
from app.utils.ashes_500 import get_ashes_500_maps

mod = Blueprint('api_cards', __name__, url_prefix='/api/cards')


@mod.route('/')
def listing():
    """Returns canonical JSON for all cards in the database"""
    cards = db.session.query(Card.id, Card.json).all()
    ashes_500_revision_id = db.session.query(Ashes500Revision.id).order_by(
        Ashes500Revision.id.desc()
    ).limit(1).scalar()
    ashes_500_map, ashes_500_combo_map = get_ashes_500_maps(ashes_500_revision_id)
    results = []
    for card in cards:
        card_json = json.loads(card.json)
        card_json['ashes_500_costs'] = ashes_500_map.get(card.id)
        card_json['ashes_500_combos'] = ashes_500_combo_map.get(card.id)
        results.append(card_json)
    return jsonify({
        'ashes_500_revision': ashes_500_revision_id,
        'cards': results
    })



@mod.route('/tts-export')
def tts_export():
    """Returns basic card data necessary for parsing Ashes.live decks into TableTop Simulator"""
    cards = db.session.query(Card.json).all()
    card_data = [json.loads(x.json) for x in cards]
    return jsonify({x['name']: x.get('placement') for x in card_data})


@mod.route('/search', methods=['POST'])
def search():
    """Returns IDs that match the given filter criteria"""
    data = request.get_json()
    query = db.session.query(Card.id)
    # Setup our filters
    include_all = data.get('includeAllCards', False)
    types = data.get('types')
    if types and 'summon' in types:
        query = query.filter(
            Card.name.like('Summon%')
        )
        types.remove('summon')
    if types and 'conjurations' in types:
        types.remove('conjurations')
        types = types + ['Conjuration', 'Conjured Alteration Spell']
    if types:
        query = query.filter(
            Card.card_type.in_(types)
        )
    elif not include_all:
        query = query.filter(
            Card.card_type.notin_(['Phoenixborn', 'Conjuration', 'Conjured Alteration Spell'])
        )
    releases = data.get('releases')
    if releases == 'phg':
        query = query.join(
            Release, Release.id == Card.release_id
        ).filter(
            Release.is_phg.is_(True)
        )
    elif releases == 'mine' and current_user.is_authenticated and current_user.collection:
        my_release_ids = [x.release_id for x in current_user.collection]
        query = query.filter(
            Card.release_id.in_(my_release_ids)
        )
    dice = data.get('dice')
    diceLogic = data.get('diceLogic', 'or')
    if dice and diceLogic == 'or':
        query = query.filter(
            Card.has_any_dice_filter(dice)
        )
    elif dice:
        query = query.filter(
            Card.has_all_dice_filter(dice)
        )
    phoenixborn = data.get('phoenixborn')
    if phoenixborn:
        query = query.filter(db.or_(
            Card.phoenixborn.is_(None),
            Card.phoenixborn == phoenixborn
        ))
    search = data.get('search')
    if search:
        # Setup prefix search so that we can get partial word matches
        terms = ''.join((search, '*')) if ' ' not in search else ''.join(('"', search, '"'))
        query = query.filter(
            FullTextSearch(terms, NameTextSearch, FullTextMode.BOOLEAN)
        )
    return jsonify(query.all())
