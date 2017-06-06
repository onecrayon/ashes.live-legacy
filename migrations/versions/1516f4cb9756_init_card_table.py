"""Init Card table

Revision ID: 1516f4cb9756
Revises: 955164ff3b89
Create Date: 2017-06-05 17:10:18.814810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1516f4cb9756'
down_revision = '955164ff3b89'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('card',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=25), nullable=False),
        sa.Column('stub', sa.String(length=25), nullable=False),
        sa.Column('release', sa.Integer(), nullable=False),
        sa.Column('card_type', sa.String(length=25), nullable=False),
        sa.Column('cost_weight', sa.Integer(), nullable=False),
        sa.Column('json', sa.Text(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_card_card_type'), 'card', ['card_type'], unique=False)
    op.create_index(op.f('ix_card_cost_weight'), 'card', ['cost_weight'], unique=False)
    op.create_index(op.f('ix_card_release'), 'card', ['release'], unique=False)
    op.create_index(op.f('ix_card_stub'), 'card', ['stub'], unique=True)
    op.execute('CREATE FULLTEXT INDEX ix_card_text ON card (name, text)')
    die_table = op.create_table('die',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cards_dice',
        sa.Column('card_id', sa.Integer(), nullable=True),
        sa.Column('die_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['card.id'], ),
        sa.ForeignKeyConstraint(['die_id'], ['die.id'], )
    )
    
    # Insert dice information
    op.bulk_insert(die_table, [
        {'name': 'Ceremonial'},
        {'name': 'Charm'},
        {'name': 'Illusion'},
        {'name': 'Natural'},
        {'name': 'Divine'},
        {'name': 'Sympathy'}
    ])


def downgrade():
    op.drop_table('cards_dice')
    op.drop_table('die')
    op.drop_index(op.f('ix_card_text'), table_name='card')
    op.drop_index(op.f('ix_card_stub'), table_name='card')
    op.drop_index(op.f('ix_card_release'), table_name='card')
    op.drop_index(op.f('ix_card_cost_weight'), table_name='card')
    op.drop_index(op.f('ix_card_card_type'), table_name='card')
    op.drop_table('card')
