"""empty message

Revision ID: 7bce4f3ac10b
Revises: 997bb4de27ba
Create Date: 2018-01-22 14:14:41.272235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bce4f3ac10b'
down_revision = '997bb4de27ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('post_id', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'post_id')
    # ### end Alembic commands ###
