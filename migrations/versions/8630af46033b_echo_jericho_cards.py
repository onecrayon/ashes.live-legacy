"""Echo and Jericho cards

Revision ID: 8630af46033b
Revises: 83bd4be85322
Create Date: 2017-11-19 21:28:23.633283

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa

from app import db
from app.models.card import Card


# revision identifiers, used by Alembic.
revision = '8630af46033b'
down_revision = '83bd4be85322'
branch_labels = None
depends_on = None


def upgrade():
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/8630af46033b_echo_jericho.json'), 'r') as f:
        data = json.load(f)
    inserts = []
    stubs = []
    for card in data:
        card_text = []
        for effect in card.get('text', []):
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
        inserts.append({
            'name': card['name'],
            'stub': card['stub'],
            'release': card['release'],
            'card_type': card['type'],
            'cost_weight': card.get('weight', 0),
            'text': ' '.join(card_text),
            'copies': card.get('copies', None)
        })
        stubs.append(card['stub'])
    op.bulk_insert(Card.__table__, inserts)
    # Gather all new cards and update JSON, dice types, and conjurations
    cards = Card.query.filter(
        Card.stub.in_(stubs)
    ).order_by(Card.id.asc()).all()
    card_data = iter(data)
    for card in cards:
        json_data = next(card_data)
        json_data['id'] = card.id
        for conjuration_name in json_data.get('conjurations', []):
            conjuration = Card.query.filter(Card.name == conjuration_name).first()
            card.conjurations.append(conjuration)
        if len(card.conjurations) and card.name.startswith('Summon'):
            card.is_summon_spell = True
        json_data['images'] = {
            'full': '/images/cards/{}.png'.format(card.stub),
            'compressed': '/images/cards/{}.jpg'.format(card.stub),
            'thumbnail': '/images/cards/{}-slice.jpg'.format(
                card.stub if not card.is_summon_spell else card.conjurations[0].stub
            )
        }
        card.dice_flags = Card.dice_to_flags(json_data.get('dice'))
        card.phoenixborn = json_data.get('phoenixborn')
        card.json = json.dumps(json_data, separators=(',', ':'), sort_keys=True)
    db.session.commit()


def downgrade():
    pass
