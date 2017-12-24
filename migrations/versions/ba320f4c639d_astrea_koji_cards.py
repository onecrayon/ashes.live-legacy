"""Astrea and Koji cards

Revision ID: ba320f4c639d
Revises: 1cdfefbe8e0f
Create Date: 2017-12-22 11:35:11.270754

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa

from app.models.card import Card

# revision identifiers, used by Alembic.
revision = 'ba320f4c639d'
down_revision = '1cdfefbe8e0f'
branch_labels = None
depends_on = None


def upgrade():
    # Fix Crimson Bomber cost typo
    connection = op.get_bind()
    # Victoria Glassfire's spellboard value is wrong
    bomber = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub AND cost_weight = 106'),
        stub='crimson-bomber'
    ).fetchone()
    if bomber:
        bomber_json = json.loads(bomber['json'])
        bomber_json['cost'] = [
            '[[main]]',
            '2 [[ceremonial:class]]'
        ]
        bomber_json['weight'] = 206
        connection.execute(
            sa.text('UPDATE card SET json = :json, cost_weight = :weight WHERE id = :id'),
            json=json.dumps(bomber_json, separators=(',', ':'), sort_keys=True),
            weight=bomber_json['weight'],
            id=bomber['id']
        )
    # Import new Astrea and Koji cards
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/ba320f4c639d_astrea_koji.json'), 'r') as f:
        data = json.load(f)
    inserts = []
    stubs = []
    # Create table stub so we can bulk_insert
    card_table = sa.table(
        'card',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=25), nullable=False),
        sa.Column('stub', sa.String(length=25), nullable=False),
        sa.Column('release', sa.Integer, nullable=False),
        sa.Column('card_type', sa.String(length=25), nullable=False),
        sa.Column('cost_weight', sa.Integer, nullable=False),
        sa.Column('text', sa.Text),
        sa.Column('copies', sa.SmallInteger, nullable=True),
        sa.Column('dice_flags', sa.Integer, nullable=False, server_default='0'),
        sa.Column('split_dice_flags', sa.Integer, nullable=False, server_default='0'),
        sa.Column('phoenixborn', sa.String(length=25), nullable=True),
        # sa.Column('json', sa.Text),
        # sa.Column('summon_id', sa.Integer, nullable=True),
        # sa.Column('is_summon_spell', sa.Boolean, nullable=False, server_default='0'),
    )
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
            'copies': card.get('copies', None),
            'dice_flags': Card.dice_to_flags(card.get('dice')),
            'split_dice_flags': Card.dice_to_flags(card.get('splitDice')),
            'phoenixborn': card.get('phoenixborn')
        })
        stubs.append(card['stub'])
    op.bulk_insert(card_table, inserts)
    # Gather all conjurations, and add image paths and IDs
    connection = op.get_bind()
    cards = connection.execute(
        sa.text('SELECT id, name, stub, json FROM card WHERE stub IN :stubs ORDER BY id ASC'),
        stubs=stubs
    ).fetchall()
    card_data = iter(data)
    for card in cards:
        json_data = next(card_data)
        json_data['id'] = card['id']
        conjurations = json_data.get('conjurations', [])
        first_conjuration_stub = None
        for conjuration_name in conjurations:
            conjuration = connection.execute(
                sa.text('SELECT id, stub FROM card WHERE name = :name'),
                name=conjuration_name
            ).fetchone()
            connection.execute(
                sa.text('UPDATE card SET summon_id = :summon_id WHERE id = :id'),
                summon_id=card['id'],
                id=conjuration['id']
            )
            if not first_conjuration_stub:
                first_conjuration_stub = conjuration['stub']
        is_summon_spell = len(conjurations) and card['name'].startswith('Summon')
        json_data['images'] = {
            'full': '/images/cards/{}.png'.format(card['stub']),
            'compressed': '/images/cards/{}.jpg'.format(card['stub']),
            'thumbnail': '/images/cards/{}-slice.jpg'.format(
                card['stub'] if not is_summon_spell else first_conjuration_stub
            )
        }
        connection.execute(
            sa.text(
                'UPDATE card SET is_summon_spell = :is_summon_spell, json = :json WHERE id = :id'
            ),
            is_summon_spell=is_summon_spell,
            json=json.dumps(json_data, separators=(',', ':'), sort_keys=True),
            id=card['id']
        )


def downgrade():
    pass
