"""Strip costs from search

Revision ID: f773f8b42f30
Revises: b81735103075
Create Date: 2018-03-12 13:56:22.486584

"""
import json
import re

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f773f8b42f30'
down_revision = 'b81735103075'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    cards = connection.execute(sa.text('SELECT id, json FROM card')).fetchall()
    for card in cards:
        json_data = json.loads(card['json'])
        card_text = []
        for effect in json_data.get('text', []):
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(
                re.sub(
                    # Costs are lowercase, so this strips all costs but leaves card references
                    r'\[\[[a-z].*?\]\]', '', effect['text']
                ).replace('[[', '').replace(']]', '')
            )
        connection.execute(
            sa.text('UPDATE card SET text = :text WHERE id = :id'),
            text=' '.join(card_text),
            id=card['id']
        )


def downgrade():
    # No need to downgrade this, since it's just an adjustment to the search text
    pass
