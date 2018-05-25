from collections import defaultdict
import json

from flask import Blueprint, jsonify, request
from sqlalchemy_fulltext import FullTextSearch
import sqlalchemy_fulltext.modes as FullTextMode

from app import db
from app.models.ashes_500 import Ashes500Revision, Ashes500Value
from app.models.card import Card, NameTextSearch

mod = Blueprint('api_cards', __name__, url_prefix='/api/cards')


@mod.route('/')
def listing():
    """Returns canonical JSON for all cards in the database"""
    cards = db.session.query(Card.id, Card.json).all()
    ashes_500_revision_id = db.session.query(Ashes500Revision.id).order_by(
        Ashes500Revision.id.desc()
    ).limit(1).scalar()
    ashes_500_values = Ashes500Value.query.filter(
        Ashes500Value.revision_id == ashes_500_revision_id
    ).all()
    ashes_500_map = defaultdict(list)
    ashes_500_combo_map = defaultdict(list)
    for values in ashes_500_values:
        ashes_500_map[values.card_id].append({
            'combo_card_id': values.combo_card_id,
            'qty_1': values.qty_1,
            'qty_2': values.qty_2,
            'qty_3': values.qty_3
        })
        if values.combo_card_id:
            ashes_500_combo_map[values.combo_card_id].append(values.card_id)
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
    if releases:
        query = query.filter(
            Card.release.in_(releases)
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
