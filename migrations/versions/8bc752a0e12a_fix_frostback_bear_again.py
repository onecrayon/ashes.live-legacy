"""Fix Frostback Bear again

Revision ID: 8bc752a0e12a
Revises: 71292fa6d3a9
Create Date: 2018-07-05 10:37:36.869863

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bc752a0e12a'
down_revision = '71292fa6d3a9'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Fixed text for Spite
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='frostback-bear'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['text'][1]['text'] = card_json['text'][1]['text'].replace(
            'When this unit deals damage to a Phoenixborn',
            'When this unit deals damage to a Phoenixborn by attacking'
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
