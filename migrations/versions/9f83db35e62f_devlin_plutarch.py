"""Devlin and Plutarch expansions

Revision ID: 9f83db35e62f
Revises: 603a770a8941
Create Date: 2020-02-01 21:37:35.521036

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa

from app.models.card import Card


# revision identifiers, used by Alembic.
revision = '9f83db35e62f'
down_revision = '603a770a8941'
branch_labels = None
depends_on = None


def upgrade():
    # Some long-ass names in these expansions...
    op.alter_column('card', 'name', type_=sa.String(30), existing_type=sa.String(25))
    op.alter_column('card', 'stub', type_=sa.String(30), existing_type=sa.String(25))

    """
    Tasks to insert cards:

    * Create text files
    * Generate JSON from text files
    * Spot fix dice/altDice where appropriate (commonly messed up)
    * Generate dice counts using JSON
    * Update JSON by hand from generated dice counts file
    * Update release mapping with the JSON release number mapped to the new release dicts
    """
    # Insert our new releases
    releases = [
        {'name': 'The Scoundrels of the Sea', 'is_phg': False, 'is_promo': False},
        {'name': 'The Mad Doctor', 'is_phg': False, 'is_promo': False},
    ]
    for release in releases:
        connection = op.get_bind()
        connection.execute(
            sa.text('INSERT INTO `releases` (name, is_phg, is_promo) VALUES (:name, :is_phg, :is_promo)'),
            **release
        )
        release['id'] = connection.execute('SELECT LAST_INSERT_ID()').scalar()
    # And finally match our release dicts to the generated release numbers in the JSON file
    release_mapping = {
        23: releases[0],
        24: releases[1],
    }

    # Import new Devlin and Plutarch cards
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/9f83db35e62f_devlin_plutarch.json'), 'r') as f:
        data = json.load(f)
    inserts = []
    stubs = []
    # Create table stub so we can bulk_insert
    card_table = sa.table(
        'card',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True, autoincrement=True),
        sa.Column('entity_id', sa.Integer, nullable=False),
        sa.Column('name', sa.String(length=25), nullable=False),
        sa.Column('stub', sa.String(length=25), nullable=False),
        sa.Column('release_id', sa.Integer, nullable=False),
        sa.Column('card_type', sa.String(length=25), nullable=False),
        sa.Column('cost_weight', sa.Integer, nullable=False),
        sa.Column('text', sa.Text),
        sa.Column('copies', sa.SmallInteger, nullable=True),
        sa.Column('dice_flags', sa.Integer, nullable=False, server_default='0'),
        sa.Column('alt_dice_flags', sa.Integer, nullable=False, server_default='0'),
        sa.Column('phoenixborn', sa.String(length=25), nullable=True),
        # sa.Column('json', sa.Text),
        # sa.Column('summon_id', sa.Integer, nullable=True),
        # sa.Column('is_summon_spell', sa.Boolean, nullable=False, server_default='0'),
    )
    # Gather entity_ids for all our new cards
    entity_ids = []
    for _ in range(0, len(data)):
        connection = op.get_bind()
        connection.execute('INSERT INTO streamable () VALUES()')
        entity_ids.append(connection.execute('SELECT LAST_INSERT_ID()').scalar())
    for idx, card in enumerate(data):
        card_text = []
        for effect in card.get('text', []):
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
        inserts.append({
            'entity_id': entity_ids[idx],
            'name': card['name'],
            'stub': card['stub'],
            'release_id': release_mapping[card['release']]['id'],
            'card_type': card['type'],
            'cost_weight': card.get('weight', 0),
            'text': ' '.join(card_text),
            'copies': card.get('copies', None),
            'dice_flags': Card.dice_to_flags(card.get('dice')),
            'alt_dice_flags': Card.dice_to_flags(card.get('altDice')),
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
        json_data['release'] = release_mapping[json_data['release']]
        conjurations = json_data.get('conjurations', [])
        first_conjuration_stub = None
        for conjuration_name in conjurations:
            conjuration = connection.execute(
                sa.text('SELECT id, stub FROM card WHERE name = :name'),
                name=conjuration_name
            ).fetchone()
            connection.execute(
                sa.text('INSERT INTO card_conjuration (card_id, conjuration_id) VALUES (:summon_id, :conjuration_id)'),
                summon_id=card['id'],
                conjuration_id=conjuration['id']
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
    op.alter_column('card', 'name', type_=sa.String(25), existing_type=sa.String(30))
    op.alter_column('card', 'stub', type_=sa.String(25), existing_type=sa.String(30))
