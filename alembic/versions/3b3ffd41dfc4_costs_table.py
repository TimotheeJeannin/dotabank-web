"""Costs table

Revision ID: 3b3ffd41dfc4
Revises: d24bbbf0e3d
Create Date: 2014-11-15 13:24:40.055599

"""

# revision identifiers, used by Alembic.
revision = '3b3ffd41dfc4'
down_revision = 'd24bbbf0e3d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('monthly_cost',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('month', sa.Date(), nullable=True),
    sa.Column('cost', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('monthly_cost')
    ### end Alembic commands ###