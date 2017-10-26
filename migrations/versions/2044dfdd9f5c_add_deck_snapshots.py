"""Add deck snapshots

Revision ID: 2044dfdd9f5c
Revises: 7d34298715dc
Create Date: 2017-10-25 20:38:22.141419

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2044dfdd9f5c'
down_revision = '7d34298715dc'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('deck', 'public', new_column_name='is_public',
                    existing_type=sa.Boolean(), existing_server_default='0', existing_nullable=False)
    op.add_column('deck', sa.Column('is_snapshot', sa.Boolean(), nullable=False))
    op.add_column('deck', sa.Column('source_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_deck_created'), 'deck', ['created'], unique=False)
    op.create_index(op.f('ix_deck_is_snapshot'), 'deck', ['is_snapshot'], unique=False)
    op.create_index(op.f('ix_deck_source_id'), 'deck', ['source_id'], unique=False)
    op.create_foreign_key('deck_ibfk_3', 'deck', 'deck', ['source_id'], ['id'])


def downgrade():
    op.alter_column('deck', 'is_public', new_column_name='public',
                    existing_type=sa.Boolean(), existing_server_default='0', existing_nullable=False)
    op.drop_constraint('deck_ibfk_3', 'deck', type_='foreignkey')
    op.drop_index(op.f('ix_deck_source_id'), table_name='deck')
    op.drop_index(op.f('ix_deck_is_snapshot'), table_name='deck')
    op.drop_index(op.f('ix_deck_created'), table_name='deck')
    op.drop_column('deck', 'source_id')
    op.drop_column('deck', 'is_snapshot')
