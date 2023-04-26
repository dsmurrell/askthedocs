"""drop field

Revision ID: 8a97d576f167
Revises: 9919cba25c1d
Create Date: 2023-04-26 21:43:08.395900

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8a97d576f167'
down_revision = '9919cba25c1d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sections', 'embedding')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sections', sa.Column('embedding', postgresql.ARRAY(sa.NUMERIC()), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
