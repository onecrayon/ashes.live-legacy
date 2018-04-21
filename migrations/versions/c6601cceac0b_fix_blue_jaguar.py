"""Fix Blue Jaguar

Revision ID: c6601cceac0b
Revises: 29e36534f30e
Create Date: 2018-04-16 13:26:48.586356

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6601cceac0b'
down_revision = '29e36534f30e'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # I'm so ehausted...
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='blue-jaguar'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['text'][0]['text'] = card_json['text'][0]['text'].replace('ehaustion', 'exhaustion')
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
