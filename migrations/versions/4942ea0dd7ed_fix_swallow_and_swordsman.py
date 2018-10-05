"""Fix Swallow and Swordsman

Revision ID: 4942ea0dd7ed
Revises: 5a89fc74e3b1
Create Date: 2018-09-15 07:29:48.358409

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4942ea0dd7ed'
down_revision = '5a89fc74e3b1'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Swallow is mis-filed as being part of the core set
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='nightshade-swallow'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['release'] = 3
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            id=card['id']
        )
    # Sonic Swordsman is missing his Aftershock number
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='sonic-swordsman'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['text'][0]['name'] = 'Aftershock 2'
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
