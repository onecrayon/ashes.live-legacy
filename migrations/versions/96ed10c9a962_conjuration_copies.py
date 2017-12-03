"""Added conjuration copies column

Revision ID: 96ed10c9a962
Revises: 8efcb18f36a7
Create Date: 2017-10-01 22:40:51.930121

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96ed10c9a962'
down_revision = '8efcb18f36a7'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    cards = connection.execute(
        sa.text('SELECT id, stub, json FROM card WHERE card_type IN :card_types'),
        card_types=['Conjuration', 'Conjured Alteration Spell']
    ).fetchall()
    for card in cards:
        card_json = json.loads(card['json'])
        json_update = None
        if card['stub'] == 'masked-wolf':
            # Masked Wolf is missing card copies (oversight from original import)
            card_json['copies'] = '5'
        elif card.stub == 'winged-lioness':
            # And so is Winged Lioness...
            card_json['copies'] = '4'
        json_update = json.dumps(card_json, separators=(',', ':'), sort_keys=True)
        connection.execute(
            sa.text('UPDATE card SET copies = :copies, json = :json WHERE id = :id'),
            copies=int(card_json['copies']),
            json=json_update,
            id=card['id']
        )


def downgrade():
    pass
