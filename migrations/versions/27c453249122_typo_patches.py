"""Typo patches

Revision ID: 27c453249122
Revises: c0b05d2841bf
Create Date: 2017-09-19 15:25:24.128602

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27c453249122'
down_revision = 'c0b05d2841bf'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # "Change of Revenge", eh?
    chant = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='change-of-revenge'
    ).fetchone()
    if chant:
        chant_json = json.loads(chant['json'])
        chant_json['name'] = 'Chant of Revenge'
        chant_json['stub'] = 'chant-of-revenge'
        chant_json['images']['full'] = '/images/cards/chant-of-revenge.png'
        chant_json['images']['compressed'] = '/images/cards/chant-of-revenge.jpg'
        chant_json['images']['thumbnail'] = '/images/cards/chant-of-revenge-slice.jpg'
        connection.execute(
            sa.text('UPDATE card SET name = :name, stub = :stub, json = :json WHERE id = :id'),
            name=chant_json['name'],
            stub=chant_json['stub'],
            json=json.dumps(chant_json, separators=(',', ':'), sort_keys=True),
            id=chant['id']
        )
    
    # I forgot when I wrote my original `is_summon_spell` logic that I considered this a summon
    widows = connection.execute(
        sa.text(
            'SELECT id, json FROM card WHERE stub = :stub AND is_summon_spell = :is_summon_spell'
        ),
        stub='summon-sleeping-widows',
        is_summon_spell=False
    ).fetchone()
    if widows:
        widows_json = json.loads(widows['json'])
        widows_json['images']['thumbnail'] = '/images/cards/sleeping-widow-slice.jpg'
        connection.execute(
            sa.text(
                'UPDATE card SET is_summon_spell = :is_summon_spell, json = :json WHERE id = :id'
            ),
            is_summon_spell=True,
            json=json.dumps(widows_json, separators=(',', ':'), sort_keys=True),
            id=widows['id']
        )
    
    # For some reason Summon Three-Eyed Owl is missing its thumbnail
    owls = connection.execute(
        sa.text(
            'SELECT id, json FROM card WHERE stub = :stub AND is_summon_spell = :is_summon_spell'
        ),
        stub='summon-three-eyed-owl',
        is_summon_spell=False
    ).fetchone()
    if owls:
        owls_json = json.loads(owls['json'])
        owls_json['images']['thumbnail'] = '/images/cards/three-eyed-owl-slice.jpg'
        owls_json['conjurations'] = ['Three-Eyed Owl']
        connection.execute(
            sa.text(
                'UPDATE card SET is_summon_spell = :is_summon_spell, json = :json WHERE id = :id'
            ),
            is_summon_spell=True,
            json=json.dumps(owls_json, separators=(',', ':'), sort_keys=True),
            id=owls['id']
        )
    
    # Simple typos
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/27c453249122_typo_patches.json'), 'r') as f:
        data = json.load(f)
    update_map = {}
    for card in data:
        card_text = []
        for effect in card.get('text', []):
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
        update_map[card['stub']] = {
            'text': ' '.join(card_text),
            'json_data': card
        }
    cards = connection.execute(
        sa.text('SELECT id, stub, json FROM card WHERE stub IN :stubs'),
        stubs=list(update_map.keys())
    ).fetchall()
    for card in cards:
        json_data = json.loads(card['json'])
        card_update = update_map[card['stub']]
        json_data.update(card_update['json_data'])
        connection.execute(
            sa.text('UPDATE card SET text = :text, json = :json WHERE id = :id'),
            text=card_update['text'],
            json=json.dumps(json_data, separators=(',', ':'), sort_keys=True),
            id=card['id']
        )


def downgrade():
    # No point in downgrading this stuff; upgrades are skipped if they have already been made
    pass
