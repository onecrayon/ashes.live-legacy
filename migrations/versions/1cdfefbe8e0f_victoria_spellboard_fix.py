"""Victoria spellboard fix

Revision ID: 1cdfefbe8e0f
Revises: 8630af46033b
Create Date: 2017-12-11 12:56:03.915387

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cdfefbe8e0f'
down_revision = '8630af46033b'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Victoria Glassfire's spellboard value is wrong
    vickie = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='victoria-glassfire'
    ).fetchone()
    if vickie:
        vickie_json = json.loads(vickie['json'])
        vickie_json['spellboard'] = 4
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            json=json.dumps(vickie_json, separators=(',', ':'), sort_keys=True),
            id=vickie['id']
        )


def downgrade():
    pass
