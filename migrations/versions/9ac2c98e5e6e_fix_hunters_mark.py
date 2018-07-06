"""Fix Hunter's Mark

Revision ID: 9ac2c98e5e6e
Revises: c3d83a74b9b1
Create Date: 2018-07-06 11:18:01.241706

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ac2c98e5e6e'
down_revision = 'c3d83a74b9b1'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Hunter's Mark is not linked to Harold for its summon ID
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='harold-westraven'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['conjurations'] = ['Hunter\'s Mark']
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            id=card['id']
        )
    conjuration = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='hunters-mark'
    ).fetchone()
    if conjuration:
        card_json = json.loads(conjuration['json'])
        card_json['copies'] = 1
        connection.execute(
            sa.text('UPDATE card SET summon_id = :summon_id, json = :json, copies = 1 WHERE id = :id'),
            summon_id=card['id'],
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            id=conjuration['id']
        )


def downgrade():
    pass
