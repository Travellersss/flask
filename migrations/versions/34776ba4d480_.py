"""empty message

Revision ID: 34776ba4d480
Revises: 8607523a74ce
Create Date: 2018-01-16 15:37:07.546408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34776ba4d480'
down_revision = '8607523a74ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('body_html', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'body_html')
    # ### end Alembic commands ###
