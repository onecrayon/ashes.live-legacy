"""Fix Exotic Gorilla

Revision ID: 603a770a8941
Revises: c64b5f213a6f
Create Date: 2020-02-01 15:28:24.409638

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '603a770a8941'
down_revision = 'c64b5f213a6f'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Used an old image for the text reference and need to update it
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='exotic-gorilla'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['text'][1]['name'] = 'Massive 1'
        card_text = []
        for effect in card_json['text']:
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
        connection.execute(
            sa.text('UPDATE card SET json = :json, text = :text WHERE id = :id'),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            text=' '.join(card_text),
            id=card['id']
        )


def downgrade():
    pass
