"""Initial migration

Revision ID: 7c035b427770
Revises: 2fb46b247001
Create Date: 2024-03-19 12:09:33.587178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c035b427770'
down_revision = '2fb46b247001'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('closed', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('closed_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.drop_column('closed_at')
        batch_op.drop_column('closed')

    # ### end Alembic commands ###
