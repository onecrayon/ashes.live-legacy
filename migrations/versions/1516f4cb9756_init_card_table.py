"""Init Card table

Revision ID: 1516f4cb9756
Revises: 955164ff3b89
Create Date: 2017-06-05 17:10:18.814810

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1516f4cb9756'
down_revision = '955164ff3b89'
branch_labels = None
depends_on = None


def upgrade():
    card_table = op.create_table('card',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=25), nullable=False),
        sa.Column('stub', sa.String(length=25), nullable=False),
        sa.Column('json', sa.Text()),
        sa.Column('release', sa.Integer(), nullable=False),
        sa.Column('card_type', sa.String(length=25), nullable=False),
        sa.Column('cost_weight', sa.Integer(), nullable=False),
        sa.Column('dice_flags', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('phoenixborn', sa.String(length=25), nullable=True),
        sa.Column('summon_id', sa.Integer(), nullable=True),
        sa.Column('copies', sa.SmallInteger(), nullable=True),
        sa.Column('is_summon_spell', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('text', sa.Text()),
        sa.ForeignKeyConstraint(['summon_id'], ['card.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_card_card_type'), 'card', ['card_type'], unique=False)
    op.create_index(op.f('ix_card_cost_weight'), 'card', ['cost_weight'], unique=False)
    op.create_index(op.f('ix_card_release'), 'card', ['release'], unique=False)
    op.create_index(op.f('ix_card_stub'), 'card', ['stub'], unique=True)
    op.create_index(op.f('ix_card_name'), 'card', ['name'], unique=True)
    op.create_index(op.f('ix_card_dice_flags'), 'card', ['dice_flags'], unique=False)
    op.create_index(op.f('ix_card_phoenixborn'), 'card', ['phoenixborn'], unique=False)
    op.execute('CREATE FULLTEXT INDEX ix_card_text ON card (name, text)')
    die_table = op.create_table('die',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stub', sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_die_stub'), 'die', ['stub'], unique=True)
    op.create_table('cards_dice',
        sa.Column('card_id', sa.Integer(), nullable=True),
        sa.Column('die_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['die_id'], ['die.id'], )
    )

    # Insert dice information
    op.bulk_insert(die_table, [
        {'stub': 'ceremonial'},
        {'stub': 'charm'},
        {'stub': 'illusion'},
        {'stub': 'natural'},
        {'stub': 'divine'},
        {'stub': 'sympathy'}
    ])

    # Insert card data
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/1516f4cb9756_initial_import.json'), 'r') as f:
        data = json.load(f)
    inserts = []
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
            'text': ' '.join(card_text)
        })
    op.bulk_insert(card_table, inserts)
    # Gather all cards and update JSON, dice types, and conjurations
    connection = op.get_bind()
    cards = connection.execute('SELECT id FROM card ORDER BY id ASC').fetchall()
    card_data = iter(data)
    for card in cards:
        json_data = next(card_data)
        json_data['id'] = card['id']
        connection.execute(
            sa.text('UPDATE card SET json = :json_string WHERE id = :id'),
            json_string=json.dumps(json_data, separators=(',', ':'), sort_keys=True),
            id=card['id']
        )
        # DISABLED: downstream update to Card model discards the usage of the Die model,
        # so I removed the code completely when I refactored migrations to decouple them from
        # model definitions (otherwise this would be impossible to rebuild from scratch, which
        # would prevent me from open sourcing it ever)
        for conjuration_name in json_data.get('conjurations', []):
            conjuration = connection.execute(
                sa.text('SELECT id FROM card WHERE name = :name'),
                name=conjuration_name
            ).fetchone()
            connection.execute(
                sa.text('UPDATE card SET summon_id = :summon_id WHERE id = :id'),
                summon_id=card['id'],
                id=conjuration['id']
            )


def downgrade():
    op.drop_table('cards_dice')
    op.drop_table('die')
    op.drop_table('card')
