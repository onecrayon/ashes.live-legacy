"""Dice to bitwise flags

Revision ID: 8efcb18f36a7
Revises: 27c453249122
Create Date: 2017-09-23 22:21:36.062441

"""
import json

from alembic import op
import sqlalchemy as sa

from app.models.card import Card

# revision identifiers, used by Alembic.
revision = '8efcb18f36a7'
down_revision = '27c453249122'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('deck_card',
        sa.Column('deck_id', sa.Integer(), nullable=False),
        sa.Column('card_id', sa.Integer(), nullable=False),
        sa.Column('count', sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('deck_id', 'card_id')
    )
    op.create_table('deck_die',
        sa.Column('deck_id', sa.Integer(), nullable=False),
        sa.Column('die_flag', sa.Integer(), nullable=False),
        sa.Column('count', sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('deck_id', 'die_flag')
    )
    op.drop_table('decks_cards')
    op.drop_table('cards_dice')
    op.drop_table('decks_dice')
    op.drop_table('die')

    # Go through all cards and set their dice flags appropriately
    connection = op.get_bind()
    cards = connection.execute('SELECT id, json FROM card').fetchall()
    for card in cards:
        card_json = json.loads(card['json'])
        connection.execute(
            sa.text(
                'UPDATE card SET dice_flags = :dice_flags, phoenixborn = :phoenixborn WHERE id = :id'
            ),
            dice_flags=Card.dice_to_flags(card_json.get('dice')),
            phoenixborn=card_json.get('phoenixborn'),
            id=card['id']
        )


def downgrade():
    op.create_table('die',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('stub', sa.String(10), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('decks_dice',
        sa.Column('deck_id', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('die_id', sa.Integer(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], name='decks_dice_ibfk_1'),
        sa.ForeignKeyConstraint(['die_id'], ['die.id'], name='decks_dice_ibfk_2')
    )
    op.create_table('cards_dice',
        sa.Column('card_id', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('die_id', sa.Integer(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], name='cards_dice_ibfk_1'),
        sa.ForeignKeyConstraint(['die_id'], ['die.id'], name='cards_dice_ibfk_2')
    )
    op.create_table('decks_cards',
        sa.Column('deck_id', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('card_id', sa.Integer(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], name='decks_cards_ibfk_1'),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], name='decks_cards_ibfk_2')
    )
    op.drop_table('deck_die')
    op.drop_table('deck_card')
