"""Init Sessions table

Revision ID: 73274bb2404e
Revises: 04ad9c5cc483
Create Date: 2017-07-14 15:05:32.063782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73274bb2404e'
down_revision = '04ad9c5cc483'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('sessions',
	    sa.Column('id', sa.Integer(), nullable=False),
	    sa.Column('session_id', sa.String(length=255), nullable=True),
	    sa.Column('data', sa.LargeBinary(), nullable=True),
	    sa.Column('expiry', sa.DateTime(), nullable=True),
	    sa.PrimaryKeyConstraint('id'),
	    sa.UniqueConstraint('session_id')
    )


def downgrade():
    op.drop_table('sessions')
