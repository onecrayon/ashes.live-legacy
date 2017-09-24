import re

from flask import Blueprint, jsonify, request
from sqlalchemy_fulltext import FullTextSearch
import sqlalchemy_fulltext.modes as FullTextMode

from app import db
from app.models.card import Card, NameTextSearch

mod = Blueprint('api_cards', __name__, url_prefix='/api/cards')


@mod.route('/')
def listing():
    return jsonify({'error': 'Coming soon?'})


@mod.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = db.session.query(Card.id)
    # Setup our filters
    types = data.get('types')
    if types:
        query = query.filter(
            Card.card_type.in_(types)
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
    # TODO: figure out how to filter out cards based on the selected Phoenixborn
    search = data.get('search')
    if search:
        # Setup prefix search so that we can get partial word matches
        terms = re.compile('[ ]+').split(search)
        terms = '* '.join(terms)
        terms = terms + '*'
        query = query.filter(db.or_(
            FullTextSearch(search, NameTextSearch, FullTextMode.NATURAL),
            FullTextSearch(terms, NameTextSearch, FullTextMode.BOOLEAN)
        ))
    return jsonify(query.all())
