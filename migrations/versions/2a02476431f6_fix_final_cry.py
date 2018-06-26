"""Fix Final Cry

Revision ID: 2a02476431f6
Revises: cd65126c65de
Create Date: 2018-06-26 09:53:49.483650

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a02476431f6'
down_revision = 'cd65126c65de'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Playin' dem "spels"
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='final-cry'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['text'][0]['text'] = card_json['text'][0]['text'].replace(
            'spel ',
            'spell '
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
