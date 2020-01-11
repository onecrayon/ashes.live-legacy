"""Fix preconstructed_release copies

Revision ID: c64b5f213a6f
Revises: 50d400ccb926
Create Date: 2020-01-11 09:55:49.293997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c64b5f213a6f'
down_revision = '50d400ccb926'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE deck SET preconstructed_release = NULL WHERE is_preconstructed = 0")


def downgrade():
    pass
