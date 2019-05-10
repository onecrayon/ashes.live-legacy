"""Fix Ashes 500 Brennen combo cost

Revision ID: 8ba02e22c972
Revises: 859c6eaea17b
Create Date: 2019-05-10 08:38:30.644479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ba02e22c972'
down_revision = '859c6eaea17b'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    brennen_id = connection.execute(
        sa.text('SELECT id FROM card WHERE stub = :stub'),
        stub='brennen-blackcloud'
    ).scalar()
    chant_id = connection.execute(
        sa.text('SELECT id FROM card WHERE stub = :stub'),
        stub='chant-of-revenge'
    ).scalar()
    combo_id = connection.execute(
        sa.text('SELECT id FROM ashes500_value WHERE card_id = :brennen AND combo_card_id = :chant'),
        brennen=brennen_id,
        chant=chant_id
    ).scalar()
    connection.execute(
        sa.text('UPDATE ashes500_value SET card_id = :chant, combo_card_id = :brennen WHERE id = :id'),
        chant=chant_id,
        brennen=brennen_id,
        id=combo_id
    )


def downgrade():
    pass
