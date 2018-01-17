"""empty message

Revision ID: 53110796d44c
Revises: ea8b419bf93b
Create Date: 2018-01-16 23:10:46.239384

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '53110796d44c'
down_revision = 'ea8b419bf93b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('body_html', sa.Text(), nullable=True))
    op.add_column('comment', sa.Column('disable', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_comment_date'), 'comment', ['date'], unique=False)
    op.drop_column('comment', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('name', mysql.VARCHAR(length=255), nullable=True))
    op.drop_index(op.f('ix_comment_date'), table_name='comment')
    op.drop_column('comment', 'disable')
    op.drop_column('comment', 'body_html')
    # ### end Alembic commands ###
