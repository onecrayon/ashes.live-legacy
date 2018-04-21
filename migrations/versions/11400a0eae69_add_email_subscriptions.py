"""Add email subscriptions

Revision ID: 11400a0eae69
Revises: c6601cceac0b
Create Date: 2018-04-21 09:14:21.907728

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '11400a0eae69'
down_revision = 'c6601cceac0b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('email_subscriptions', sa.Boolean(), nullable=False))
    op.create_index(op.f('ix_user_email_subscriptions'), 'user', ['email_subscriptions'], unique=False)


def downgrade():
    op.drop_column('user', 'email_subscriptions')
