"""Add Phoenix section

Revision ID: 71cabd32c148
Revises: 8ba02e22c972
Create Date: 2019-05-18 11:09:46.646371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71cabd32c148'
down_revision = '8ba02e22c972'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Update PDF links to local copies
    description = connection.execute(
        sa.text('SELECT description FROM section WHERE stub = :stub'),
        stub='rules'
    ).scalar()
    description = description.replace(
        'https://www.plaidhatgames.com/images/games/ashes/rules.pdf',
        'https://ashes.live/files/ashes-core-rules.pdf'
    ).replace(
        'https://www.plaidhatgames.com/images/games/ashes/faq20.pdf',
        'https://ashes.live/files/ashes-official-faq.pdf'
    )
    connection.execute(
        sa.text('UPDATE section SET description = :description WHERE stub = :stub'),
        description=description,
        stub='rules'
    )
    # Create new section
    connection.execute('INSERT INTO streamable () VALUES()')
    entity_id = connection.execute('SELECT LAST_INSERT_ID()').scalar()
    connection.execute(
        sa.text(
            'INSERT INTO section (title, stub, is_restricted, entity_id, description) '
            'VALUES (:title, :stub, :is_restricted, :entity_id, :description)'
        ),
        title='Project Phoenix',
        stub='phoenix',
        is_restricted=False,
        entity_id=entity_id,
        description="""[[Project Phoenix ashes.live/phoenix/]] is a collaboration of Ashes fans working together to continue development on this wonderful game."""
    )


def downgrade():
    pass
