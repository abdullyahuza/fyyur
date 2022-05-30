"""empty message

Revision ID: afc1c8597e9c
Revises: facd6cf925fa
Create Date: 2022-05-30 11:35:59.961325

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'afc1c8597e9c'
down_revision = 'facd6cf925fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('availability_list')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('availability_list',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('artistID', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('startTime', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('endTime', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artistID'], ['artists.id'], name='availability_list_artistID_fkey'),
    sa.PrimaryKeyConstraint('id', name='availability_list_pkey'),
    sa.UniqueConstraint('endTime', name='availability_list_endTime_key'),
    sa.UniqueConstraint('startTime', name='availability_list_startTime_key')
    )
    # ### end Alembic commands ###
