"""Ashes 500 May 2019

Revision ID: 859c6eaea17b
Revises: 8d5e80852841
Create Date: 2019-05-09 10:48:13.343683

"""
from datetime import datetime
import json
import os.path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '859c6eaea17b'
down_revision = '8d5e80852841'
branch_labels = None
depends_on = None


def upgrade():
    # Populate initial Ashes 500 data
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/859c6eaea17b_ashes_500_may_2019.json'), 'r') as f:
        data = json.load(f)
    connection = op.get_bind()
    connection.execute('INSERT INTO streamable () VALUES()')
    entity_id = connection.execute('SELECT LAST_INSERT_ID()').scalar()
    description = connection.execute(
        'SELECT description FROM ashes500_revision ORDER BY id DESC LIMIT 1'
    ).scalar()
    # Update link
    description = description.replace(
        'https://docs.google.com/spreadsheets/d/1_VGzVoAU5k7JsG3N56WL1Nno3DCSUvWm5eZp6gzlqk0/edit?usp=sharing',
        'https://docs.google.com/spreadsheets/d/12HsQO47Nj9GykadM5q2ETfjvoN3OuEjd9xmqanTD08I/edit?usp=sharing'
    )
    connection.execute(
        sa.text(
            'INSERT INTO ashes500_revision (entity_id, created, description) '
            'VALUES (:entity_id, :created, :description)'
        ),
        entity_id=entity_id,
        created=datetime.utcnow(),
        description=description
    )
    # Create table stub so we can bulk_insert
    op.add_column('ashes500_value', sa.Column('combo_card_type', sa.String(25), nullable=True))
    value_table = sa.table(
        'ashes500_value',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True, autoincrement=True),
        sa.Column('card_id', sa.Integer, nullable=False),
        sa.Column('revision_id', sa.Integer, nullable=False),
        sa.Column('combo_card_id', sa.Integer, nullable=True),
        sa.Column('combo_card_type', sa.String(25), nullable=True),
        sa.Column('qty_1', sa.SmallInteger, nullable=False),
        sa.Column('qty_2', sa.SmallInteger, nullable=True),
        sa.Column('qty_3', sa.SmallInteger, nullable=True),
    )
    revision_id = connection.execute('SELECT id FROM ashes500_revision ORDER BY id DESC LIMIT 1').scalar()
    cards = connection.execute('SELECT id, stub FROM card').fetchall()
    stub_map = {x['stub']: x['id'] for x in cards}
    card_values = [{
        'card_id': stub_map[x['stub']],
        'revision_id': revision_id,
        'combo_card_id': stub_map[x['combo_stub']] if x.get('combo_stub') else None,
        'combo_card_type': x.get('combo_card_type'),
        'qty_1': x.get('qty_1'),
        'qty_2': x.get('qty_2'),
        'qty_3': x.get('qty_3')
    } for x in data]
    op.bulk_insert(value_table, card_values)


def downgrade():
    op.drop_column('ashes500_values', 'combo_card_type')
