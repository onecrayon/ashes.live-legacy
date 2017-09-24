"""Dice to bitwise flags

Revision ID: 8efcb18f36a7
Revises: 27c453249122
Create Date: 2017-09-23 22:21:36.062441

"""
import json

from alembic import op
import sqlalchemy as sa

from app import db
from app.models.card import Card

# revision identifiers, used by Alembic.
revision = '8efcb18f36a7'
down_revision = '27c453249122'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('deck_card',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('deck_id', sa.Integer(), nullable=False),
        sa.Column('card_id', sa.Integer(), nullable=False),
        sa.Column('count', sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deck_card_deck_id'), 'deck_card', ['deck_id'], unique=False)
    op.create_table('deck_die',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('deck_id', sa.Integer(), nullable=False),
        sa.Column('die_flag', sa.Integer(), nullable=False),
        sa.Column('count', sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deck_die_deck_id'), 'deck_die', ['deck_id'], unique=False)
    op.drop_table('decks_cards')
    op.drop_table('cards_dice')
    op.drop_table('decks_dice')
    op.drop_table('die')
    op.add_column('card', sa.Column('dice_flags', sa.Integer(), nullable=False))
    op.add_column('card', sa.Column('phoenixborn', sa.String(length=25), nullable=True))
    op.create_index(op.f('ix_card_dice_flags'), 'card', ['dice_flags'], unique=False)
    op.create_index(op.f('ix_card_phoenixborn'), 'card', ['phoenixborn'], unique=False)

    # Go through all cards and set their dice flags appropriately
    cards = Card.query.all()
    for card in cards:
        card_json = json.loads(card.json)
        card.dice_flags = Card.dice_to_flags(card_json.get('dice'))
        card.phoenixborn = card_json.get('phoenixborn')
    db.session.commit()


def downgrade():
    op.drop_index(op.f('ix_card_dice_flags'), table_name='card')
    op.drop_index(op.f('ix_card_phoenixborn'), table_name='card')
    op.drop_column('card', 'phoenixborn')
    op.drop_column('card', 'dice_flags')
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
