"""Add many-to-many conjurations

Revision ID: 8d5e80852841
Revises: 3028ef1e3335
Create Date: 2019-03-13 13:31:20.665390

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8d5e80852841'
down_revision = '3028ef1e3335'
branch_labels = None
depends_on = None


def upgrade():
    conjuration_table = op.create_table('card_conjuration',
        sa.Column('card_id', sa.Integer(), nullable=False),
        sa.Column('conjuration_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['conjuration_id'], ['card.id'], ),
        sa.PrimaryKeyConstraint('card_id', 'conjuration_id')
    )
    connection = op.get_bind()
    cards = connection.execute(
        'SELECT id, summon_id FROM card WHERE summon_id IS NOT NULL'
    ).fetchall()
    inserts = [
        {'card_id': x['summon_id'], 'conjuration_id': x['id']} for x in cards
    ]
    # And fix up Rising Horde
    rising_horde = connection.execute(
        sa.text('SELECT id FROM card WHERE stub = :stub'),
        stub='rising-horde'
    ).fetchone()
    fallen = connection.execute(
        sa.text('SELECT id FROM card WHERE stub = :stub'),
        stub='fallen'
    ).fetchone()
    inserts.append({
        'card_id': rising_horde['id'],
        'conjuration_id': fallen['id']
    })
    op.bulk_insert(conjuration_table, inserts)
    # Drop old summon_id column
    op.drop_constraint('card_ibfk_1', 'card', type_='foreignkey')
    op.drop_column('card', 'summon_id')


def downgrade():
    op.add_column('card', sa.Column('summon_id', sa.Integer(), autoincrement=False, nullable=True))
    op.create_foreign_key('card_ibfk_1', 'card', 'card', ['summon_id'], ['id'])
    connection = op.get_bind()
    relations = connection.execute('SELECT * FROM card_conjuration').fetchall()
    rising_horde = connection.execute(
        sa.text('SELECT id FROM card WHERE stub = :stub'),
        stub='rising-horde'
    ).fetchone()
    for relation in relations:
        if relation['card_id'] != rising_horde['id']:
            connection.execute(
                sa.text('UPDATE card SET summon_id = :summon_id WHERE id = :id'),
                id=relation['conjuration_id'],
                summon_id=relation['card_id']
            )
    op.drop_table('card_conjuration')
