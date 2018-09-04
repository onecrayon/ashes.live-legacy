"""Fix Stream indices

Revision ID: 5a89fc74e3b1
Revises: 5bc042a1c94d
Create Date: 2018-09-04 11:07:46.112926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a89fc74e3b1'
down_revision = '5bc042a1c94d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_stream_entity_type'), 'stream', ['entity_type'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_stream_entity_type'), table_name='stream')
