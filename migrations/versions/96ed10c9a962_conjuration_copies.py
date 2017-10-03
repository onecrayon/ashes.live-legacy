"""Added conjuration copies column

Revision ID: 96ed10c9a962
Revises: 8efcb18f36a7
Create Date: 2017-10-01 22:40:51.930121

"""
import json

from alembic import op
import sqlalchemy as sa

from app import db
from app.models.card import Card


# revision identifiers, used by Alembic.
revision = '96ed10c9a962'
down_revision = '8efcb18f36a7'
branch_labels = None
depends_on = None


def upgrade():
    cards = Card.query.filter(
        Card.card_type.in_(['Conjuration', 'Conjured Alteration Spell'])
    ).all()
    for card in cards:
        card_json = json.loads(card.json)
        if card.stub == 'masked-wolf':
            # Masked Wolf is missing card copies (oversight from original import)
            card_json['copies'] = '5'
            card.json = json.dumps(card_json)
        elif card.stub == 'winged-lioness':
            # And so is Winged Lioness...
            card_json['copies'] = '4'
            card.json = json.dumps(card_json)
        card.copies = int(card_json['copies'])
    db.session.commit()


def downgrade():
    pass
