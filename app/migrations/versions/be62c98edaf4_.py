"""empty message

Revision ID: be62c98edaf4
Revises: 104fd46b6b3e
Create Date: 2019-05-03 13:18:27.236441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be62c98edaf4'
down_revision = '104fd46b6b3e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('review', sa.Column('review', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('review', 'review')
    # ### end Alembic commands ###