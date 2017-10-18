"""Fix Owl Conjuration

Revision ID: 7d34298715dc
Revises: 96ed10c9a962
Create Date: 2017-10-18 10:16:50.886835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d34298715dc'
down_revision = '96ed10c9a962'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
       "UPDATE card AS conjuration JOIN card AS summon ON summon.stub = 'summon-three-eyed-owl'"
       " SET conjuration.summon_id = summon.id"
       " WHERE conjuration.stub = 'three-eyed-owl'"
    )


def downgrade():
    pass
