"""Card image paths and errata

Revision ID: c0b05d2841bf
Revises: 712bbd7aaefa
Create Date: 2017-09-11 15:12:49.086051

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa

from app import db
from app.models.card import Die, Card


# revision identifiers, used by Alembic.
revision = 'c0b05d2841bf'
down_revision = '712bbd7aaefa'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('card', sa.Column('is_summon_spell', sa.Boolean(), nullable=False, server_default='0'))

    # Grab our card errata from FAQ 2.0 (2017)
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/c0b05d2841bf_errata_2017.json'), 'r') as f:
        data = json.load(f)
    update_map = {}
    for card in data:
        card_text = []
        for effect in card.get('text', []):
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
        update_map[card['name']] = {
            'cost_weight': card.get('weight', 0),
            'text': ' '.join(card_text),
            'json_data': card
        }
    # Gather all cards and update image paths, is_summon_spell, and errata (if any)
    cards = Card.query.options(db.joinedload('conjurations')).all()
    for card in cards:
        json_data = json.loads(card.json)
        if card.name in update_map:
            card_update = update_map[card.name]
            card.cost_weight = card_update['cost_weight']
            card.text = card_update['text']
            json_data.update(card_update['json_data'])
        # NOTE: if reusing this logic, only check for the conjurations and startswith('Summon')!
        # Otherwise we miss things like Summon Sleeping Widows
        if card.card_type == 'Ready Spell' and len(card.conjurations) and card.name.startswith('Summon'):
            card.is_summon_spell = True
        json_data['images'] = {
            'full': '/images/cards/{}.png'.format(card.stub),
            'compressed': '/images/cards/{}.jpg'.format(card.stub)
        }
        thumbnail_path = '/images/cards/{}-slice.jpg'.format(
            card.stub if not card.is_summon_spell else card.conjurations[0].stub
        )
        real_image = os.path.realpath(os.path.join(my_dir, '../../app/static/', thumbnail_path.lstrip('/')))
        if os.path.exists(real_image):
            json_data['images']['thumbnail'] = thumbnail_path
        card.json = json.dumps(json_data, separators=(',', ':'), sort_keys=True)
    db.session.commit()


def downgrade():
    op.drop_column('card', 'is_summon_spell')
