"""Add session number and change defaults on created_at and updated_at

Revision ID: 807be8ba48a9
Revises: dc8c2480dc23
Create Date: 2023-04-23 14:01:57.056899

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "807be8ba48a9"
down_revision = "dc8c2480dc23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "documents", ["id"])
    op.add_column("sections", sa.Column("number", sa.Integer(), nullable=False))
    op.add_column("sections", sa.Column("text", sa.Text(), nullable=False))
    op.create_unique_constraint(None, "sections", ["id"])
    op.drop_column("sections", "content")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "sections", sa.Column("content", sa.TEXT(), autoincrement=False, nullable=False)
    )
    op.drop_constraint(None, "sections", type_="unique")
    op.drop_column("sections", "text")
    op.drop_column("sections", "number")
    op.drop_constraint(None, "documents", type_="unique")
    # ### end Alembic commands ###
