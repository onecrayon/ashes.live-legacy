"""User descriptions and precon decks

Revision ID: 83bd4be85322
Revises: 2044dfdd9f5c
Create Date: 2017-11-10 13:57:33.140786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83bd4be85322'
down_revision = '2044dfdd9f5c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('deck', sa.Column('is_preconstructed', sa.Boolean(), nullable=False, server_default='0'))
    op.create_index(op.f('ix_deck_is_preconstructed'), 'deck', ['is_preconstructed'], unique=False)
    op.add_column('user', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('user', 'is_admin')
    op.drop_column('user', 'description')
    op.drop_column('deck', 'is_preconstructed')
