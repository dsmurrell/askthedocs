"""Add document and section

Revision ID: c6e076350021
Revises:
Create Date: 2023-04-22 00:13:24.388031

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "c6e076350021"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "documents",
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_table(
        "sections",
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("document_id", sa.String(length=255), nullable=False),
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sections")
    op.drop_table("documents")
    # ### end Alembic commands ###