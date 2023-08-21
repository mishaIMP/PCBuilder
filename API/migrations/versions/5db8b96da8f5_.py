"""empty message

Revision ID: 5db8b96da8f5
Revises: 
Create Date: 2023-08-17 14:31:38.316818

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5db8b96da8f5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('public_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('total_price', sa.Integer(), nullable=True),
    sa.Column('author', sa.String(length=255), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('title', sa.String(length=50), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('additional_components',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('component', sa.String(), nullable=False),
    sa.Column('model', sa.String(length=255), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('link', sa.String(length=255), nullable=True),
    sa.Column('public_info_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['public_info_id'], ['public_info.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('components',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('component', sa.String(), nullable=False),
    sa.Column('model', sa.String(length=255), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('link', sa.String(length=255), nullable=True),
    sa.Column('public_info_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['public_info_id'], ['public_info.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('components')
    op.drop_table('additional_components')
    op.drop_table('public_info')
    op.drop_table('users')
    # ### end Alembic commands ###