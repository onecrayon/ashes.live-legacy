"""Init Posts and Sections

Revision ID: 9dc9e7b1e96e
Revises: 313bc8d9f4e1
Create Date: 2018-04-06 20:47:35.949587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9dc9e7b1e96e'
down_revision = '11400a0eae69'
branch_labels = None
depends_on = None


def upgrade():
    section_table = op.create_table('section',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('stub', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_restricted', sa.Boolean(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_section_is_restricted'), 'section', ['is_restricted'], unique=False)
    op.create_index(op.f('ix_section_stub'), 'section', ['stub'], unique=True)
    op.create_index(op.f('ix_section_entity_id'), 'section', ['entity_id'], unique=True)
    op.create_table('post',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('section_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('pin_teaser', sa.Text(), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_moderated', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('original_title', sa.String(length=255), nullable=True),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('moderation_notes', sa.Text(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True, server_default=sa.text(
            'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
        )),
        sa.ForeignKeyConstraint(['section_id'], ['section.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_is_deleted'), 'post', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_post_is_pinned'), 'post', ['is_pinned'], unique=False)
    op.create_index(op.f('ix_post_created'), 'post', ['created'], unique=False)
    op.create_index(op.f('ix_post_entity_id'), 'post', ['entity_id'], unique=True)
    op.create_index(op.f('ix_post_section_id'), 'post', ['section_id'], unique=False)
    op.execute('CREATE FULLTEXT INDEX ix_post_text ON post (title, text)')
    # Create default sections
    entity_ids = []
    for _ in range(0, 4):
        connection = op.get_bind()
        connection.execute('INSERT INTO streamable () VALUES()')
        entity_ids.append(connection.execute('SELECT LAST_INSERT_ID()').scalar())
    op.bulk_insert(section_table, [
        {
            'title': 'Site News', 'stub': 'news', 'is_restricted': True, 'entity_id': entity_ids[0],
            'description': (
                'Ever wondered about the minutiae of every update to Ashes.live? Wonder no longer!'
            )
        },
        {
            'title': 'General', 'stub': 'general', 'is_restricted': False,
            'entity_id': entity_ids[1],
            'description': (
                'General discussion about Ashes; if it doesn\'t fit elsewhere, post it here!'
            )
        },
        {
            'title': 'Rules', 'stub': 'rules', 'is_restricted': False, 'entity_id': entity_ids[2],
            'description': """Have a rules question or clarification about Ashes? Post it here!

* [[Official Ashes Rules https://www.plaidhatgames.com/images/games/ashes/rules.pdf]] (PDF)
* [[Official Ashes FAQ https://www.plaidhatgames.com/images/games/ashes/faq20.pdf]] (PDF)
* [[Unofficial Ashes Rules Reference ashes.live/files/ashes-rules-reference.pdf]] (PDF)"""
        },
        {
            'title': 'Strategy', 'stub': 'strategy', 'is_restricted': False,
            'entity_id': entity_ids[3],
            'description': (
                'Have or need advice on demolishing your opponents? '
                'You\'ve come to the right place!'
            )
        }
    ])


def downgrade():
    op.drop_table('post')
    op.drop_table('section')
