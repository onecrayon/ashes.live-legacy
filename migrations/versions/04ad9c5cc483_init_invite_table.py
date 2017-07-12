"""Init Invite table

Revision ID: 04ad9c5cc483
Revises: 1516f4cb9756
Create Date: 2017-07-12 12:06:55.700833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04ad9c5cc483'
down_revision = '1516f4cb9756'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('invite',
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=254), nullable=False),
        sa.Column('requests', sa.Integer(), nullable=False),
        sa.Column('requested', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_invite_email'), 'invite', ['email'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_invite_email'), table_name='invite')
    op.drop_table('invite')
