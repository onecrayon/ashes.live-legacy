"""Errata 2018

Revision ID: 5bc042a1c94d
Revises: e33dd7d9efcb
Create Date: 2018-08-01 14:35:57.380486

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5bc042a1c94d'
down_revision = 'e33dd7d9efcb'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Grab our card errata from FAQ 3.0 (2018)
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/5bc042a1c94d_errata_2018.json'), 'r') as f:
        data = json.load(f)
    stub_map = {x['stub']: x for x in data}
    cards = connection.execute(
        sa.text('SELECT id, json, stub, version FROM card WHERE stub IN :stubs'),
        stubs=tuple(stub_map.keys())
    ).fetchall()
    for card in cards:
        card_text = []
        card_json = json.loads(card['json'])
        new_card = stub_map.get(card['stub'], {})
        for effect in new_card.get('text', []):
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
        card_json['text'] = new_card.get('text', [])
        connection.execute(
            sa.text('UPDATE card SET text = :text, json = :json, version = :version WHERE id = :id'),
            id=card['id'],
            text=' '.join(card_text),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            version=card['version'] + 1
        )


def downgrade():
    pass
