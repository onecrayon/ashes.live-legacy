"""Init User table

Revision ID: 955164ff3b89
Revises: 
Create Date: 2017-05-04 21:38:18.505608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '955164ff3b89'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=254), nullable=False),
        sa.Column('badge', sa.String(length=8), nullable=False),
        sa.Column('username', sa.String(42), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_badge'), 'user', ['badge'], unique=True)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_badge'), table_name='user')
    op.drop_table('user')
