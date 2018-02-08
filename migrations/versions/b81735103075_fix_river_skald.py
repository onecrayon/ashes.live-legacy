"""Fix River Skald

Revision ID: b81735103075
Revises: f4c336a8ffa6
Create Date: 2018-02-08 10:43:17.248809

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b81735103075'
down_revision = 'f4c336a8ffa6'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # River Skald has 3 life, not 2
    skald = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='river-skald'
    ).fetchone()
    if skald:
        skald_json = json.loads(skald['json'])
        skald_json['life'] = 3
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            json=json.dumps(skald_json, separators=(',', ':'), sort_keys=True),
            id=skald['id']
        )


def downgrade():
    pass
