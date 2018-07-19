"""Fix Sonic Swordsman

Revision ID: e33dd7d9efcb
Revises: b0499e19f839
Create Date: 2018-07-19 15:16:19.779196

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e33dd7d9efcb'
down_revision = 'b0499e19f839'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Let's pace some tokens, shall we?
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='sonic-swordsman'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['text'][0]['text'] = card_json['text'][0]['text'].replace('pace  wound', 'place 2 wound')
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
