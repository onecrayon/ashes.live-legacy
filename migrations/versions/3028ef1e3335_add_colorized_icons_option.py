"""Add colorized icons option

Revision ID: 3028ef1e3335
Revises: 172799711283
Create Date: 2019-03-13 12:10:16.670505

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3028ef1e3335'
down_revision = '172799711283'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('colorize_icons', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('user', 'colorize_icons')
