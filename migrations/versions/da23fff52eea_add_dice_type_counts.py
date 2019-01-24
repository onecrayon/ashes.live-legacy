"""Add dice type counts

Revision ID: da23fff52eea
Revises: 9dc9e7b1e96e
Create Date: 2018-05-18 09:39:30.092729

"""
import json
import os.path

from alembic import op
import sqlalchemy as sa

from app.models.card import Card


# revision identifiers, used by Alembic.
revision = 'da23fff52eea'
down_revision = '5afab7189e03'
branch_labels = None
depends_on = None


def upgrade():
    # Rename our split_dice_flags column to reflect its new broader usage
    op.alter_column('card', 'split_dice_flags', nullable=False, server_default='0',
                    existing_type=sa.Integer, new_column_name='alt_dice_flags')
    my_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(my_dir, '../data/da23fff52eea_dice_counts.json'), 'r') as f:
        data = json.load(f)
    # Update JSON with new naming and magic costs
    connection = op.get_bind()
    cards = connection.execute('SELECT id, stub, json FROM card').fetchall()
    for card in cards:
        card_json = json.loads(card['json'])
        # Rename splitDice to altDice, because we are storing more than parallel costs
        if card_json.get('splitDice'):
            card_json['altDice'] = card_json['splitDice']
            del card_json['splitDice']
        if data.get(card['stub']):
            card_json.update(data[card['stub']])
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            id=card['id']
        )
    # Spot fixes for cards that incorrectly had alternate dice as their dice requirements
    cards = connection.execute(
        sa.text('SELECT id, json, dice_flags FROM card WHERE stub IN :stubs'),
        stubs=('rins-fury', 'drain-vitality', 'summon-orchid-dove', 'frost-bite')
    ).fetchall()
    for card in cards:
        card_json = json.loads(card['json'])
        # Abort if the fix has already been applied
        if not card_json.get('dice'):
            continue
        card_json['altDice'] = card_json['dice']
        del card_json['dice']
        connection.execute(
            sa.text(
                'UPDATE card SET json = :json, dice_flags = :dice_flags, '
                'alt_dice_flags = :alt_dice_flags '
                'WHERE id = :id'
            ),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            dice_flags=0,
            alt_dice_flags=card['dice_flags'],
            id=card['id']
        )
    # Spot fix for Royal Charm, which doesn't require any sort of dice currently
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='royal-charm'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['altDice'] = ['charm', 'divine']
        connection.execute(
            sa.text(
                'UPDATE card SET json = :json, alt_dice_flags = :alt_dice_flags '
                'WHERE id = :id'
            ),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            alt_dice_flags=Card.dice_to_flags(card_json['altDice']),
            id=card['id']
        )
    # Spot fix for Angelic Rescue, which improperly requires Divine
    card = connection.execute(
        sa.text('SELECT id, json FROM card WHERE stub = :stub'),
        stub='angelic-rescue'
    ).fetchone()
    if card:
        card_json = json.loads(card['json'])
        card_json['dice'] = ['illusion']
        card_json['altDice'] = ['divine']
        connection.execute(
            sa.text(
                'UPDATE card SET json = :json, dice_flags = :dice_flags, '
                'alt_dice_flags = :alt_dice_flags '
                'WHERE id = :id'
            ),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            dice_flags=Card.dice_to_flags(card_json['dice']),
            alt_dice_flags=Card.dice_to_flags(card_json['altDice']),
            id=card['id']
        )
    # Spot fix for Hollow, which improperly marks both dice types as required
    card = connection.execute(
        sa.text('SELECT id, json, dice_flags FROM card WHERE stub = :stub'),
        stub='hollow'
    ).fetchone()
    if card and card['dice_flags']:
        card_json = json.loads(card['json'])
        del card_json['dice']
        connection.execute(
            sa.text(
                'UPDATE card SET json = :json, dice_flags = :dice_flags '
                'WHERE id = :id'
            ),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            dice_flags=0,
            id=card['id']
        )
    # Add support for first five tracking
    op.create_table('deck_selected_card',
        sa.Column('deck_id', sa.Integer(), nullable=False),
        sa.Column('card_id', sa.Integer(), nullable=False),
        sa.Column('is_first_five', sa.Boolean(), nullable=False),
        sa.Column('is_paid_effect', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], ),
        sa.PrimaryKeyConstraint('deck_id', 'card_id')
    )


def downgrade():
    op.alter_column('card', 'alt_dice_flags', nullable=False, server_default='0',
                    existing_type=sa.Integer, new_column_name='split_dice_flags')
    # Revert JSON
    connection = op.get_bind()
    cards = connection.execute('SELECT id, json FROM card').fetchall()
    for card in cards:
        card_json = json.loads(card['json'])
        # Rename splitDice to altDice, because we are storing more than parallel costs
        if card_json.get('altDice'):
        	card_json['splitDice'] = card_json['altDice']
        	del card_json['altDice']
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            json=json.dumps(card_json, separators=(',', ':'), sort_keys=True),
            id=card['id']
        )
    op.drop_table('deck_selected_card')
