"""Added Phoenix Dice tracking

Revision ID: 83611d9fa9e0
Revises: 71cabd32c148
Create Date: 2019-06-08 10:26:09.077368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83611d9fa9e0'
down_revision = '71cabd32c148'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('phoenix_dice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=254), nullable=False),
        sa.Column('only_official_icons', sa.Boolean(), nullable=False),
        sa.Column('desired_sets', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phoenix_dice_email'), 'phoenix_dice', ['email'], unique=True)
    op.create_index(op.f('ix_phoenix_dice_only_official_icons'), 'phoenix_dice', ['only_official_icons'])


def downgrade():
    op.drop_index(op.f('ix_phoenix_dice_email'), table_name='phoenix_dice')
    op.drop_index(op.f('ix_phoenix_dice_only_official_icons'), table_name='phoenix_dice')
    op.drop_table('phoenix_dice')
