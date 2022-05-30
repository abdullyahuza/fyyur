"""empty message

Revision ID: facd6cf925fa
Revises: 8138e5b16b32
Create Date: 2022-05-30 10:09:24.856475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'facd6cf925fa'
down_revision = '8138e5b16b32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'availability_list', ['startTime'])
    op.create_unique_constraint(None, 'availability_list', ['endTime'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'availability_list', type_='unique')
    op.drop_constraint(None, 'availability_list', type_='unique')
    # ### end Alembic commands ###
