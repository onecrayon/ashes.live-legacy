"""Convert stats to numbers

Revision ID: f4c336a8ffa6
Revises: ba320f4c639d
Create Date: 2018-01-05 10:01:03.754321

"""
import json
import re

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4c336a8ffa6'
down_revision = 'ba320f4c639d'
branch_labels = None
depends_on = None


def upgrade():
    # Gather all cards and update stats to use integers wherever possible
    connection = op.get_bind()
    cards = connection.execute(
        'SELECT id, json FROM card'
    ).fetchall()
    for card in cards:
        json_data = json.loads(card['json'])
        for key, value in json_data.items():
            # Convert to int if the value is a string that only contains digits
            if isinstance(value, str) and re.search(r'^\d+$', value):
                json_data[key] = int(value)
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            id=card['id'],
            json=json.dumps(json_data, separators=(',', ':'), sort_keys=True)
        )



def downgrade():
    pass
