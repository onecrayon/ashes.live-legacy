"""User password reset column

Revision ID: e34c61cf485e
Revises: 73274bb2404e
Create Date: 2017-07-15 15:32:18.415014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e34c61cf485e'
down_revision = '73274bb2404e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('reset_uuid', sa.String(length=36), nullable=True))
    op.create_index(op.f('ix_user_reset_uuid'), 'user', ['reset_uuid'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_user_reset_uuid'), table_name='user')
    op.drop_column('user', 'reset_uuid')
