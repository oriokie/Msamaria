"""Add alias_name to Member model

Revision ID: 8f51010eb1ad
Revises: 8bfc7f2aa538
Create Date: 2024-08-31 07:10:44.628108

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f51010eb1ad'
down_revision = '8bfc7f2aa538'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.add_column(sa.Column('alias_name_1', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('alias_name_2', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.drop_column('alias_name_2')
        batch_op.drop_column('alias_name_1')

    # ### end Alembic commands ###
