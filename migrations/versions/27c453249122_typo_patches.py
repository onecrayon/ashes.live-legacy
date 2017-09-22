"""Typo patches

Revision ID: 27c453249122
Revises: c0b05d2841bf
Create Date: 2017-09-19 15:25:24.128602

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa

from app import db
from app.models.card import Card


# revision identifiers, used by Alembic.
revision = '27c453249122'
down_revision = 'c0b05d2841bf'
branch_labels = None
depends_on = None


def upgrade():
    # "Change of Revenge", eh?
    chant = Card.query.filter(Card.stub == 'change-of-revenge').first()
    if chant:
        chant_json = json.loads(chant.json)
        chant.name = 'Chant of Revenge'
        chant.stub = 'chant-of-revenge'
        chant_json['name'] = chant.name
        chant_json['stub'] = chant.stub
        chant_json['images']['full'] = '/images/cards/chant-of-revenge.png'
        chant_json['images']['compressed'] = '/images/cards/chant-of-revenge.jpg'
        chant_json['images']['thumbnail'] = '/images/cards/chant-of-revenge-slice.jpg'
        chant.json = json.dumps(chant_json)
    
    # I forgot when I wrote my `is_summon_spell` logic that I considered this a summon spell
    widows = Card.query.filter(
        Card.stub == 'summon-sleeping-widows',
        Card.is_summon_spell.is_(False)
    ).first()
    if widows:
        widows.is_summon_spell = True
        widows_json = json.loads(widows.json)
        widows_json['images']['thumbnail'] = '/images/cards/sleeping-widow-slice.jpg'
        widows.json = json.dumps(widows_json)
    
    # For some reason Summon Three-Eyed Owl is missing its thumbnail
    owls = Card.query.filter(
        Card.stub == 'summon-three-eyed-owl',
        Card.is_summon_spell.is_(False)
    ).first()
    if owls:
        owls.is_summon_spell = True
        owls_json = json.loads(owls.json)
        owls_json['images']['thumbnail'] = '/images/cards/three-eyed-owl-slice.jpg'
        owls_json['conjurations'] = ['Three-Eyed Owl']
        owls.json = json.dumps(owls_json)
    
    # Simple typos
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/27c453249122_typo_patches.json'), 'r') as f:
        data = json.load(f)
    update_map = {}
    for card in data:
        card_text = []
        for effect in card.get('text', []):
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
        update_map[card['stub']] = {
            'text': ' '.join(card_text),
            'json_data': card
        }
    cards = Card.query.filter(
        Card.stub.in_(list(update_map.keys()))
    ).all()
    for card in cards:
        json_data = json.loads(card.json)
        card_update = update_map[card.stub]
        card.text = card_update['text']
        json_data.update(card_update['json_data'])
        card.json = json.dumps(json_data, separators=(',', ':'), sort_keys=True)

    # And commit our fixes
    db.session.commit()


def downgrade():
    # No point in downgrading this stuff; upgrades are skipped if they have already been made
    pass
