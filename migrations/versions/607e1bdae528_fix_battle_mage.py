"""Fix Battle Mage

Revision ID: 607e1bdae528
Revises: 9dc9e7b1e96e
Create Date: 2018-05-24 09:17:02.351409

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '607e1bdae528'
down_revision = '9dc9e7b1e96e'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Physical card text is different from the image text
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='battle-mage'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['text'][0]['text'] = card_json['text'][0]['text'].replace(
            'When this unit attacks or counters',
            'When this unit deals damage by attacking or countering'
        )
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
