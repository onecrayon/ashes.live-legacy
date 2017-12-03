"""Echo and Jericho cards

Revision ID: 8630af46033b
Revises: 83bd4be85322
Create Date: 2017-11-19 21:28:23.633283

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa

from app.models.card import Card


# revision identifiers, used by Alembic.
revision = '8630af46033b'
down_revision = '83bd4be85322'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('card', sa.Column('split_dice_flags', sa.Integer(), nullable=False, server_default='0'))
    op.create_index(op.f('ix_card_split_dice_flags'), 'card', ['split_dice_flags'], unique=False)
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/8630af46033b_echo_jericho.json'), 'r') as f:
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
    op.drop_index('ix_card_split_dice_flags', 'card')
    op.drop_column('card', 'split_dice_flags')
