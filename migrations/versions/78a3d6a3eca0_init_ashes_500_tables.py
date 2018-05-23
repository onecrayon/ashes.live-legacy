"""Init Ashes 500 tables

Revision ID: 78a3d6a3eca0
Revises: 9dc9e7b1e96e
Create Date: 2018-05-22 14:18:57.749458

"""
from datetime import datetime
import json
import os.path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78a3d6a3eca0'
down_revision = '9dc9e7b1e96e'
branch_labels = None
depends_on = None


def upgrade():
    revision_table = op.create_table('ashes500_revision',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ashes500_revision_entity_id'), 'ashes500_revision', ['entity_id'], unique=False)
    value_table = op.create_table('ashes500_value',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('card_id', sa.Integer(), nullable=False),
        sa.Column('revision_id', sa.Integer(), nullable=False),
        sa.Column('combo_card_id', sa.Integer(), nullable=True),
        sa.Column('qty_1', sa.SmallInteger(), nullable=False),
        sa.Column('qty_2', sa.SmallInteger(), nullable=True),
        sa.Column('qty_3', sa.SmallInteger(), nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['combo_card_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['revision_id'], ['ashes500_revision.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ashes500_value_card_id'), 'ashes500_value', ['card_id'], unique=False)
    op.create_index(op.f('ix_ashes500_value_revision_id'), 'ashes500_value', ['revision_id'], unique=False)
    op.add_column('deck', sa.Column('ashes_500_revision_id', sa.Integer(), nullable=True))
    op.add_column('deck', sa.Column('ashes_500_score', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_ashes_500_revision_id', 'deck', 'ashes500_revision', ['ashes_500_revision_id'], ['id'])
    # Populate initial Ashes 500 data
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/78a3d6a3eca0_ashes_500.json'), 'r') as f:
        data = json.load(f)
    connection = op.get_bind()
    connection.execute('INSERT INTO streamable () VALUES()')
    entity_id = connection.execute('SELECT LAST_INSERT_ID()').scalar()
    op.bulk_insert(revision_table, [{
        'entity_id': entity_id,
        'created': datetime.utcnow(),
        'description': """**Ashes 500** is an alternate constructed format for Ashes [[originally created by Elliot Kramer http://www.strangecopy.com/index.php/2017/03/19/ashes-500/]] and now maintained by [[doktarr#0a=m]] with input from the community. In Ashes 500 all cards are assigned point values, and your deck must cost 500 points or less (while following all standard deck construction rules). Originally provided [[as a spreadsheet https://docs.google.com/spreadsheets/d/14vX5nkIR2_2gcxIOn8X1-cnt18v1VFr2H70xB6FXfNs/edit#gid=0]], you can now construct Ashes 500 decks here on Ashes.live.

Ashes 500 costs are formatted like **25/15/10** where the first copy of the card costs **25** points, the second copy costs **15** points, and the third copy costs **10** points (so if you included 3x copies, you would spend **25 + 15 + 10 = 50** points).

Additionally, a small number of cards include penalties when they are included together, represented by a "**!**" next to the prices. Tap or mouse over the "**!**" to view relevant penalties for that card; for instance, if your deck includes both [[Shifting Mist]] and [[Summon Butterfly Monk]], an extra 20 points will be added to the deck's total. Penalties are used to discourage overly strong archetypes and combos from standard constructed.

**Why use Ashes 500?** The Ashes 500 format encourages creative deck construction with cards that would not normally be competitive, and is a great way to shake up your local meta if you find yourselves falling into a rut.

If you would like to suggest changes to Ashes 500 prices, you can join the conversation about it in the [[#500 Slack channel http://www.strangecopy.com/index.php/ashes-chat/]] or [[post your thoughts here on Ashes.live ashes.live/posts/general/submit/]]."""
    }])
    revision_id = connection.execute('SELECT id FROM ashes500_revision').scalar()
    cards = connection.execute('SELECT id, stub FROM card').fetchall()
    stub_map = {x['stub']: x['id'] for x in cards}
    card_values = [{
        'card_id': stub_map[x['stub']],
        'revision_id': revision_id,
        'combo_card_id': stub_map[x['combo_stub']] if x.get('combo_stub') else None,
        'qty_1': x.get('qty_1'),
        'qty_2': x.get('qty_2'),
        'qty_3': x.get('qty_3')
    } for x in data]
    op.bulk_insert(value_table, card_values)


def downgrade():
    op.drop_column('deck', 'ashes_500_score')
    op.drop_constraint('fk_ashes_500_revision_id', 'deck', type_='foreignkey')
    op.drop_column('deck', 'ashes_500_revision_id')
    op.drop_table('ashes500_value')
    op.drop_table('ashes500_revision')
