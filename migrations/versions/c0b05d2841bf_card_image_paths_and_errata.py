"""Card image paths and errata

Revision ID: c0b05d2841bf
Revises: 712bbd7aaefa
Create Date: 2017-09-11 15:12:49.086051

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0b05d2841bf'
down_revision = '712bbd7aaefa'
branch_labels = None
depends_on = None


def upgrade():
    # Grab our card errata from FAQ 2.0 (2017)
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/c0b05d2841bf_errata_2017.json'), 'r') as f:
        data = json.load(f)
    update_map = {}
    for card in data:
        card_text = []
        for effect in card.get('text', []):
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
        update_map[card['stub']] = {
            'cost_weight': card.get('weight', 0),
            'text': ' '.join(card_text),
            'json_data': card
        }
    # Gather all cards and update image paths, is_summon_spell, and errata (if any)
    connection = op.get_bind()
    cards = connection.execute(
        'SELECT card.*, COUNT(conj.id) AS conjuration_count, '
        'GROUP_CONCAT(conj.stub SEPARATOR \',\') AS conjuration_stubs '
        'FROM card AS card '
        'LEFT OUTER JOIN card AS conj ON conj.summon_id = card.id '
        'GROUP BY card.id'
    ).fetchall()
    for card in cards:
        json_data = json.loads(card['json'])
        updates = {}
        if card['stub'] in update_map:
            card_update = update_map[card['stub']]
            updates['cost_weight'] = card_update['cost_weight']
            updates['text'] = card_update['text']
            json_data.update(card_update['json_data'])
        if card['conjuration_count'] and card['name'].startswith('Summon'):
            updates['is_summon_spell'] = True
        json_data['images'] = {
            'full': '/images/cards/{}.png'.format(card['stub']),
            'compressed': '/images/cards/{}.jpg'.format(card['stub'])
        }
        if updates.get('is_summon_spell') and card['conjuration_stubs']:
            stubs = card['conjuration_stubs'].split(',')
            thumbnail_path = '/images/cards/{}-slice.jpg'.format(stubs[0])
        else:
            thumbnail_path = '/images/cards/{}-slice.jpg'.format(card['stub'])
        json_data['images']['thumbnail'] = thumbnail_path
        updates['json'] = json.dumps(json_data, separators=(',', ':'), sort_keys=True)
        set_clause = ', '.join(['{key} = :{key}'.format(key=key) for key in iter(updates)])
        updates['id'] = card['id']
        connection.execute(
            sa.text('UPDATE card SET {} WHERE id = :id'.format(set_clause)),
            **updates
        )


def downgrade():
    pass
