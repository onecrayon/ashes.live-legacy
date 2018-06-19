"""Ashes 500 June 2018

Revision ID: cd65126c65de
Revises: 78a3d6a3eca0
Create Date: 2018-06-19 13:33:02.784963

"""
from datetime import datetime
import json
import os.path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd65126c65de'
down_revision = '78a3d6a3eca0'
branch_labels = None
depends_on = None


def upgrade():
     # Populate initial Ashes 500 data
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/cd65126c65de_ashes_500_june_2018.json'), 'r') as f:
        data = json.load(f)
    connection = op.get_bind()
    connection.execute('INSERT INTO streamable () VALUES()')
    entity_id = connection.execute('SELECT LAST_INSERT_ID()').scalar()
    description = connection.execute(
        'SELECT description FROM ashes500_revision ORDER BY id DESC LIMIT 1'
    ).scalar()
    # Update link and outdated value string
    description = description.replace(
        'https://docs.google.com/spreadsheets/d/14vX5nkIR2_2gcxIOn8X1-cnt18v1VFr2H70xB6FXfNs/edit?usp=sharing',
        'https://docs.google.com/spreadsheets/d/1_VGzVoAU5k7JsG3N56WL1Nno3DCSUvWm5eZp6gzlqk0/edit?usp=sharing'
    ).replace(
        'an extra 20 points', 'an extra 30 points'
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
    value_table = sa.table(
        'ashes500_value',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True, autoincrement=True),
        sa.Column('card_id', sa.Integer, nullable=False),
        sa.Column('revision_id', sa.Integer, nullable=False),
        sa.Column('combo_card_id', sa.Integer, nullable=True),
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
        'qty_1': x.get('qty_1'),
        'qty_2': x.get('qty_2'),
        'qty_3': x.get('qty_3')
    } for x in data]
    op.bulk_insert(value_table, card_values)


def downgrade():
    pass
