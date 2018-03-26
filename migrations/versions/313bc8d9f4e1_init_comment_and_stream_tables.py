"""Init Comment and Stream tables

Revision ID: 313bc8d9f4e1
Revises: f773f8b42f30
Create Date: 2018-03-15 16:18:28.405893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '313bc8d9f4e1'
down_revision = 'f773f8b42f30'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('streamable',
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('entity_id')
    )
    op.create_table('stream',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=16), nullable=True),
        sa.Column('source_entity_id', sa.Integer(), nullable=False),
        sa.Column('posted', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stream_entity_id'), 'stream', ['entity_id'], unique=True)
    op.create_index(op.f('ix_stream_souce_entity_id'), 'stream', ['source_entity_id'], unique=False)
    op.create_index(op.f('ix_stream_posted'), 'stream', ['posted'], unique=False)
    op.create_table('comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source_entity_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(length=16), nullable=True),
        sa.Column('source_version', sa.Integer(), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_moderated', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('moderation_notes', sa.Text(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True, server_default=sa.text(
            'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
        )),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comment_entity_id'), 'comment', ['entity_id'], unique=True)
    op.create_index(op.f('ix_comment_source_entity_id'), 'comment', ['source_entity_id'], unique=False)
    op.create_index(op.f('ix_comment_created'), 'comment', ['created'], unique=False)
    op.create_index(op.f('ix_comment_order'), 'comment', ['order'], unique=False)
    op.create_index(op.f('ix_comment_is_deleted'), 'comment', ['is_deleted'], unique=False)
    op.create_table('subscription',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source_entity_id', sa.Integer(), nullable=False),
        sa.Column('last_seen_entity_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'source_entity_id')
    )
    op.create_index(op.f('ix_subscription_last_seen_entity_id'), 'subscription', ['last_seen_entity_id'], unique=False)
    op.add_column('card', sa.Column('entity_id', sa.Integer(), nullable=False))
    op.add_column('card', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('deck', sa.Column('entity_id', sa.Integer(), nullable=False))
    op.add_column('user', sa.Column('exclude_subscriptions', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('is_banned', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('ban_notes', sa.Text(), nullable=True))
    # Go through Card and Deck and generate initial entity_ids
    connection = op.get_bind()
    cards = connection.execute('SELECT id FROM card ORDER BY id ASC').fetchall()
    for card in cards:
        connection.execute('INSERT INTO streamable () VALUES()')
        connection.execute(sa.text(
            'UPDATE card SET entity_id = LAST_INSERT_ID() WHERE id = :id'
        ), id=card['id'])
    decks = connection.execute('SELECT id FROM deck ORDER BY id ASC').fetchall()
    for deck in decks:
        connection.execute('INSERT INTO streamable () VALUES()')
        connection.execute(sa.text(
            'UPDATE deck SET entity_id = LAST_INSERT_ID() WHERE id = :id'
        ), id=deck['id'])
    op.create_index(op.f('ix_card_entity_id'), 'card', ['entity_id'], unique=True)
    op.create_index(op.f('ix_deck_entity_id'), 'deck', ['entity_id'], unique=True)
    # Create our initial stream (initially just a listing of all published decks)
    connection.execute(
        "INSERT INTO stream (entity_id, entity_type, source_entity_id, posted) "
        "SELECT MAX(deck.entity_id) AS entity_id, 'deck' AS entity_type, source.entity_id AS source_entity_id, "
            "MAX(deck.created) AS posted "
        "FROM deck "
        "INNER JOIN deck AS source ON source.id = deck.source_id "
        "WHERE deck.is_snapshot = 1 AND deck.is_public = 1 "
        "GROUP BY deck.source_id"
    )
    # Subscribe users to their public decks
    connection.execute(
        'INSERT INTO subscription (user_id, source_entity_id, last_seen_entity_id) '
        'SELECT deck.user_id, deck.entity_id AS source_entity_id, MAX(snapshots.entity_id) AS last_seen_entity_id '
        'FROM deck '
        'INNER JOIN deck AS snapshots ON snapshots.source_id = deck.id '
        'WHERE deck.is_snapshot = 0 AND snapshots.is_snapshot = 1 AND snapshots.is_public = 1 '
        'GROUP BY deck.id'
    )


def downgrade():
    op.drop_column('user', 'is_banned')
    op.drop_column('user', 'ban_notes')
    op.drop_column('user', 'exclude_subscriptions')
    op.drop_column('deck', 'entity_id')
    op.drop_column('card', 'version')
    op.drop_column('card', 'entity_id')
    op.drop_table('subscription')
    op.drop_table('comment')
    op.drop_table('stream')
    op.drop_table('streamable')
