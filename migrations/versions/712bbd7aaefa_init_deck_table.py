"""Init Deck table

Revision ID: 712bbd7aaefa
Revises: e34c61cf485e
Create Date: 2017-08-25 15:22:40.435669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '712bbd7aaefa'
down_revision = 'e34c61cf485e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('deck',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('public', sa.Boolean(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phoenixborn_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['phoenixborn_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deck_modified'), 'deck', ['modified'], unique=False)
    op.create_index(op.f('ix_deck_phoenixborn_id'), 'deck', ['phoenixborn_id'], unique=False)
    op.create_index(op.f('ix_deck_public'), 'deck', ['public'], unique=False)
    op.create_index(op.f('ix_deck_title'), 'deck', ['title'], unique=False)
    op.create_index(op.f('ix_deck_user_id'), 'deck', ['user_id'], unique=False)
    op.create_table('decks_cards',
        sa.Column('deck_id', sa.Integer(), nullable=True),
        sa.Column('card_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], )
    )
    op.create_table('decks_dice',
        sa.Column('deck_id', sa.Integer(), nullable=True),
        sa.Column('die_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], ),
        sa.ForeignKeyConstraint(['die_id'], ['die.id'], )
    )


def downgrade():
    op.drop_table('decks_dice')
    op.drop_table('decks_cards')
    op.drop_index(op.f('ix_deck_title'), table_name='deck')
    op.drop_index(op.f('ix_deck_public'), table_name='deck')
    op.drop_index(op.f('ix_deck_modified'), table_name='deck')
    op.drop_table('deck')
