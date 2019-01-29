"""Fix Chant of Revenge

Revision ID: 3290868ef97e
Revises: da23fff52eea
Create Date: 2019-01-29 15:37:41.464527

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3290868ef97e'
down_revision = 'da23fff52eea'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Chant of Revenge is the only card without a capitalized "Of"
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='chant-of-revenge'
    ).fetchone()
    if card:
        name = 'Chant Of Revenge'
        card_json = json.loads(card['json'])
        card_json['name'] = name
        connection.execute(
            sa.text('UPDATE card SET json = :json, name= :name WHERE id = :id'),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            name=name,
            id=card['id']
        )
    # Golden Veil has a typo in its effect text ("ot" not "of")
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='golden-veil'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['text'][0]['text'] = card_json['text'][0]['text'].replace(' ot ', ' of ')
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            id=card['id']
        )


def downgrade():
    pass
