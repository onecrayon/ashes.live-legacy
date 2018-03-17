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
        sa.Column('posted', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stream_entity_id'), 'stream', ['entity_id'], unique=True)
    op.create_index(op.f('ix_stream_posted'), 'stream', ['posted'], unique=False)
    op.create_table('comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source_entry_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(length=16), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True, server_default=sa.text(
            'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
        )),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comment_created'), 'comment', ['created'], unique=False)
    op.create_index(op.f('ix_comment_entity_id'), 'comment', ['entity_id'], unique=True)
    op.create_index(op.f('ix_comment_modified'), 'comment', ['modified'], unique=False)
    op.create_index(op.f('ix_comment_source_entry_id'), 'comment', ['source_entry_id'], unique=False)
    op.create_table('subscription',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'entity_id')
    )
    op.create_table('user_stream',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('is_delivered', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'entity_id')
    )
    op.create_index(op.f('ix_user_stream_is_delivered'), 'user_stream', ['is_delivered'], unique=False)
    op.add_column('card', sa.Column('entity_id', sa.Integer(), nullable=False))
    op.add_column('deck', sa.Column('entity_id', sa.Integer(), nullable=False))
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
        "INSERT INTO stream (entity_id, entity_type, posted) "
        "SELECT source.entity_id, 'deck' AS entity_type, MAX(deck.created) AS posted FROM deck "
        "INNER JOIN deck AS source ON source.id = deck.source_id "
        "WHERE deck.is_snapshot = 1 AND deck.is_public = 1 "
        "GROUP BY deck.source_id"
    )
    # Subscribe users to their public decks
    connection.execute(
        'INSERT INTO subscription (user_id, entity_id, created) '
        'SELECT deck.user_id, deck.entity_id, NOW() AS created FROM deck '
        'INNER JOIN deck AS snapshots ON snapshots.source_id = deck.id '
        'WHERE deck.is_snapshot = 0 AND snapshots.is_snapshot = 1 AND snapshots.is_public = 1 '
        'GROUP BY deck.id'
    )


def downgrade():
    op.drop_column('deck', 'entity_id')
    op.drop_column('card', 'entity_id')
    op.drop_table('user_stream')
    op.drop_table('subscription')
    op.drop_table('comment')
    op.drop_table('stream')
    op.drop_table('streamable')