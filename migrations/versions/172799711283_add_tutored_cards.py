"""Add tutored cards

Revision ID: 172799711283
Revises: 3290868ef97e
Create Date: 2019-03-13 10:39:42.673683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '172799711283'
down_revision = '3290868ef97e'
branch_labels = None
depends_on = None


def upgrade():
    # Drop our primary key, then recreate with the new column
    op.drop_constraint('deck_selected_card_ibfk_1', 'deck_selected_card', type_='foreignkey')
    op.drop_constraint('deck_selected_card_ibfk_2', 'deck_selected_card', type_='foreignkey')
    op.drop_constraint('PRIMARY', 'deck_selected_card', type_='primary')
    op.add_column('deck_selected_card', sa.Column('tutor_card_id', sa.Integer(), nullable=False,
                  server_default='0'))
    op.create_primary_key(None, 'deck_selected_card', ['deck_id', 'card_id', 'tutor_card_id'])
    # And finally add our foreign key constraints back
    op.create_foreign_key('deck_selected_card_ibfk_1', 'deck_selected_card', 'card', ['card_id'], ['id'])
    op.create_foreign_key('deck_selected_card_ibfk_2', 'deck_selected_card', 'deck', ['deck_id'], ['id'])


def downgrade():
    op.drop_constraint('deck_selected_card_ibfk_1', 'deck_selected_card', type_='foreignkey')
    op.drop_constraint('deck_selected_card_ibfk_2', 'deck_selected_card', type_='foreignkey')
    op.drop_constraint('PRIMARY', 'deck_selected_card', type_='primary')
    op.drop_column('deck_selected_card', 'tutor_card_id')
    op.create_primary_key(None, 'deck_selected_card', ['deck_id', 'card_id'])
    op.create_foreign_key('deck_selected_card_ibfk_1', 'deck_selected_card', 'card', ['card_id'], ['id'])
    op.create_foreign_key('deck_selected_card_ibfk_2', 'deck_selected_card', 'deck', ['deck_id'], ['id'])
