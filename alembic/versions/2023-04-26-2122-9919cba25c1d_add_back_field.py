"""add back field

Revision ID: 9919cba25c1d
Revises: af528ad9780b
Create Date: 2023-04-26 21:22:31.015938

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9919cba25c1d'
down_revision = 'af528ad9780b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sections', sa.Column('embedding', sa.ARRAY(sa.Numeric()), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sections', 'embedding')
    # ### end Alembic commands ###
