"""Init Release table

Revision ID: 18da61e6bb59
Revises: 83611d9fa9e0
Create Date: 2019-08-24 16:30:49.378760

"""
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '18da61e6bb59'
down_revision = '83611d9fa9e0'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    release_table = op.create_table('releases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=60), nullable=False),
        sa.Column('is_phg', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_promo', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('designer_name', sa.String(length=100), nullable=True),
        sa.Column('designer_url', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    # Populate the release table
    op.bulk_insert(release_table, [
        {'name': 'Core Set', 'is_phg': True},
        {'name': 'The Frostdale Giants', 'is_phg': True},
        {'name': 'The Children of Blackcloud', 'is_phg': True},
        {'name': 'The Roaring Rose', 'is_phg': True},
        {'name': 'The Duchess of Deception', 'is_phg': True},
        {'name': 'The Laws of Lions', 'is_phg': True},
        {'name': 'The Song of Soaksend', 'is_phg': True},
        {'name': 'The Masters of Gravity', 'is_phg': True},
        {'name': 'The Path of Assassins', 'is_phg': True},
        {'name': 'The Goddess of Ishra', 'is_phg': True},
        {'name': 'The Boy Among Wolves', 'is_phg': True},
        {'name': 'The Demons of Darmas', 'is_phg': True},
        {'name': 'The Spirits of Memoria', 'is_phg': True},
        {'name': 'The Ghost Guardian', 'is_phg': True},
        {'name': 'The King of Titans', 'is_phg': True},
        {'name': 'The Protector of Argaia', 'is_phg': True},
        {'name': 'The Grave King', 'is_phg': True},
        {'name': 'Dimona Odinstar (promo)', 'is_phg': True, 'is_promo': True},
        {'name': 'Lulu Firststone (promo)', 'is_phg': True, 'is_promo': True},
        {'name': 'Orrick Gilstream (promo)', 'is_phg': True, 'is_promo': True},
    ])
    # Renumber release IDs in the card table
    connection.execute('UPDATE card SET `release` = `release` + 1 WHERE `release` < 100')
    # Resetting 101 down to index 18
    connection.execute('UPDATE card SET `release` = `release` - 83 WHERE `release` > 100')
    # Update card JSON to include the release information
    release_dicts = connection.execute('SELECT * FROM releases')
    release_mapping = {x.id: x for x in release_dicts}
    cards = connection.execute(
        'SELECT id, json, `release` FROM card'
    ).fetchall()
    for card in cards:
        json_data = json.loads(card['json'])
        release_data = release_mapping.get(card['release'])
        if not release_data:
            continue
        json_data['release'] = {
            'id': release_data['id'],
            'name': release_data['name'],
            'is_phg': True if release_data['is_phg'] else False,
            'is_promo': True if release_data['is_promo'] else False
        }
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            id=card['id'],
            json=json.dumps(json_data, separators=(',', ':'), sort_keys=True)
        )
    # Create the user_release relationship table
    op.create_table('user_release',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('release_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['release_id'], ['releases.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'release_id')
    )
    # New and missing indices
    op.create_index(op.f('ix_user_release_user_id'), 'user_release', ['user_id'], unique=False)
    op.create_index(op.f('ix_ashes500_revision_created'), 'ashes500_revision', ['created'], unique=False)
    # New and renamed columns on `card`
    op.add_column('card', sa.Column('artist_name', sa.String(length=100), nullable=True))
    op.add_column('card', sa.Column('artist_url', sa.String(length=255), nullable=True))
    op.alter_column('card', 'release', new_column_name='release_id',
                    existing_type=sa.Integer(), existing_server_default='0', existing_nullable=False)
    op.drop_index('ix_card_release', table_name='card')
    op.create_index(op.f('ix_card_release_id'), 'card', ['release_id'], unique=False)
    op.create_foreign_key('card_release_ibfk_1', 'card', 'releases', ['release_id'], ['id'])
    # New column on `deck`
    op.add_column('deck', sa.Column('preconstructed_release', sa.Integer(), nullable=True))
    # Populate the preconstructed-to-release mappings
    connection.execute(
        'UPDATE deck '
        'INNER JOIN releases ON releases.name = deck.title '
        'SET deck.preconstructed_release = releases.id '
        'WHERE deck.is_preconstructed = 1 AND deck.is_public = 1 AND deck.is_snapshot = 1'
    )
    op.create_index(op.f('ix_deck_preconstructed_release'), 'deck', ['preconstructed_release'], unique=False)
    # Rename some indices now that the columns have different names
    op.drop_index('ix_card_split_dice_flags', table_name='card')
    op.create_index(op.f('ix_card_alt_dice_flags'), 'card', ['alt_dice_flags'], unique=False)
    op.drop_index('ix_deck_public', table_name='deck')
    op.create_index(op.f('ix_deck_is_public'), 'deck', ['is_public'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_deck_is_public'), table_name='deck')
    op.create_index('ix_deck_public', 'deck', ['is_public'], unique=False)
    op.drop_index(op.f('ix_card_alt_dice_flags'), table_name='card')
    op.create_index('ix_card_split_dice_flags', 'card', ['alt_dice_flags'], unique=False)
    op.drop_constraint('card_release_ibfk_1', 'card', type_='foreignkey')
    op.drop_index(op.f('ix_card_release_id'), table_name='card')
    op.drop_column('deck', 'preconstructed_release')
    # Renumber release IDs in the card table
    connection = op.get_bind()
    connection.execute('UPDATE card SET release_id = release_id + 83 WHERE release_id > 17')
    connection.execute('UPDATE card SET release_id = release_id - 1 WHERE release_id < 18')
    # Revert the card JSON release data
    # Update card JSON to include the release information
    release_dicts = connection.execute('SELECT * FROM releases')
    release_mapping = {
        'Core Set': 0,
        'The Frostdale Giants': 1,
        'The Children of Blackcloud': 2,
        'The Roaring Rose': 3,
        'The Duchess of Deception': 4,
        'The Laws of Lions': 5,
        'The Song of Soaksend': 6,
        'The Masters of Gravity': 7,
        'The Path of Assassins': 8,
        'The Goddess of Ishra': 9,
        'The Boy Among Wolves': 10,
        'The Demons of Darmas': 11,
        'The Spirits of Memoria': 12,
        'The Ghost Guardian': 13,
        'The King of Titans': 14,
        'The Protector of Argaia': 15,
        'The Grave King': 16,
        'Dimona Odinstar (promo)': 101,
        'Lulu Firststone (promo)': 102,
        'Orrick Gilstream (promo)': 103,
    }
    cards = connection.execute(
        'SELECT id, json FROM card'
    ).fetchall()
    for card in cards:
        json_data = json.loads(card['json'])
        release_id = release_mapping.get(json_data.get('release', {}).get('name', ''))
        if release_id is None:
            continue
        json_data['release'] = release_id
        connection.execute(
            sa.text('UPDATE card SET json = :json WHERE id = :id'),
            id=card['id'],
            json=json.dumps(json_data, separators=(',', ':'), sort_keys=True)
        )
    op.alter_column('card', 'release_id', new_column_name='release',
                    existing_type=sa.Integer(), existing_server_default='0', existing_nullable=False)
    op.create_index('ix_card_release', 'card', ['release'], unique=False)
    op.drop_column('card', 'artist_url')
    op.drop_column('card', 'artist_name')
    op.drop_index(op.f('ix_ashes500_revision_created'), table_name='ashes500_revision')
    op.drop_index(op.f('ix_user_release_user_id'), table_name='user_release')
    op.drop_table('user_release')
    op.drop_table('releases')
