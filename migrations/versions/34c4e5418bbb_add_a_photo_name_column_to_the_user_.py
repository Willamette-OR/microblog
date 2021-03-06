"""Add a photo name column to the user model

Revision ID: 34c4e5418bbb
Revises: 6e9b20226850
Create Date: 2018-05-01 21:01:17.485423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34c4e5418bbb'
down_revision = '6e9b20226850'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('photo_name', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'photo_name')
    # ### end Alembic commands ###
