"""Add a photo modification time to the user model

Revision ID: 30d85dfb5bd8
Revises: 34c4e5418bbb
Create Date: 2018-05-03 20:40:49.282536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30d85dfb5bd8'
down_revision = '34c4e5418bbb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('photo_mod_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'photo_mod_time')
    # ### end Alembic commands ###
