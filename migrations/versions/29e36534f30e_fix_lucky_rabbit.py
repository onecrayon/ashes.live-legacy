"""Fix Lucky Rabbit

Revision ID: 29e36534f30e
Revises: 9dc9e7b1e96e
Create Date: 2018-04-11 09:27:59.196316

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29e36534f30e'
down_revision = '313bc8d9f4e1'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Good ol' exhausted poool
    rabbit = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='lucky-rabbit'
    ).fetchone()
    if rabbit:
        rabbit_json = json.loads(rabbit['json'])
        rabbit_json['text'][0]['text'] = rabbit_json['text'][0]['text'].replace('poool', 'pool')
        card_text = []
        for effect in rabbit_json['text']:
            if 'name' in effect:
                card_text.append(effect['name'])
            card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
        connection.execute(
            sa.text('UPDATE card SET json = :json, text = :text WHERE id = :id'),
            json=json.dumps(rabbit_json, separators=(',', ':'), sort_keys=True),
            text=' '.join(card_text),
            id=rabbit['id']
        )


def downgrade():
    pass
