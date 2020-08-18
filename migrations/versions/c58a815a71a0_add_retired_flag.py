"""Add retired flag

Revision ID: c58a815a71a0
Revises: 9f83db35e62f
Create Date: 2020-08-17 20:05:59.329307

"""
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c58a815a71a0'
down_revision = '9f83db35e62f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('card', 'name', existing_type=mysql.VARCHAR(length=30), nullable=False)
    op.alter_column('card', 'stub', existing_type=mysql.VARCHAR(length=30), nullable=False)
    op.add_column('releases', sa.Column('is_retiring', sa.Boolean(), nullable=False))

    op.execute("""
    UPDATE releases SET is_retiring = TRUE WHERE name IN (
        'The Path of Assassins',
        'Dimona Odinstar (promo)',
        'Lulu Firststone (promo)',
        'Orrick Gilstream (promo)'
    ) OR is_phg IS FALSE
    """)

    # Update card JSON to include new release information
    connection = op.get_bind()
    release_dicts = connection.execute('SELECT * FROM releases')
    release_mapping = {x.id: x for x in release_dicts}
    cards = connection.execute(
        'SELECT id, json, release_id FROM card'
    ).fetchall()
    for card in cards:
        json_data = json.loads(card['json'])
        release_data = release_mapping.get(card['release_id'])
        if not release_data:
            continue
        json_data['release']['is_retiring'] = True if release_data['is_retiring'] else False
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            id=card['id'],
            json=json.dumps(json_data, separators=(',', ':'), sort_keys=True)
        )


def downgrade():
    op.drop_column('releases', 'is_retiring')
    op.alter_column('card', 'stub', existing_type=mysql.VARCHAR(length=30), nullable=True)
    op.alter_column('card', 'name', existing_type=mysql.VARCHAR(length=30), nullable=True)
