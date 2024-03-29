"""Initial migration

Revision ID: 92e4fc13a6e1
Revises: a75dd9e7928a
Create Date: 2024-03-20 17:24:19.898232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92e4fc13a6e1'
down_revision = 'a75dd9e7928a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###
