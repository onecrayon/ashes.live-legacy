"""Fix Angel's Embrace

Revision ID: b0499e19f839
Revises: 9ac2c98e5e6e
Create Date: 2018-07-10 15:52:19.949245

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0499e19f839'
down_revision = '9ac2c98e5e6e'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Angel's Embrace is not linked to Angelic Rescue for its summon ID
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='angelic-rescue'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['conjurations'] = ['Angel\'s Embrace']
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            id=card['id']
        )
    conjuration = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='angels-embrace'
    ).fetchone()
    if conjuration:
        connection.execute(
            sa.text('UPDATE card SET summon_id = :summon_id WHERE id = :id'),
            summon_id=card['id'],
            id=conjuration['id']
        )


def downgrade():
    pass
