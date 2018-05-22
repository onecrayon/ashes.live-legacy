"""Init Ashes 500 tables

Revision ID: 78a3d6a3eca0
Revises: 9dc9e7b1e96e
Create Date: 2018-05-22 14:18:57.749458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78a3d6a3eca0'
down_revision = '9dc9e7b1e96e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ashes500_revision',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ashes500_revision_entity_id'), 'ashes500_revision', ['entity_id'], unique=False)
    op.create_table('ashes500_value',
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
    op.create_foreign_key(None, 'deck', 'ashes500_revision', ['ashes_500_revision_id'], ['id'])


def downgrade():
    op.drop_column('deck', 'ashes_500_score')
    op.drop_column('deck', 'ashes_500_revision_id')
    op.drop_table('ashes500_value')
    op.drop_table('ashes500_revision')
