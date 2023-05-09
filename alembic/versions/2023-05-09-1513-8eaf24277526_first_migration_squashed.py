"""first_migration_squashed

Revision ID: 8eaf24277526
Revises: 
Create Date: 2023-05-09 15:13:12.660226

"""
import pgvector
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "8eaf24277526"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "documents",
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("hash", sa.String(length=64), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("text_no_html", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=22), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
        sa.UniqueConstraint("hash"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_table(
        "questions",
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("body_username", sa.String(length=100), nullable=True),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("query_string", sa.Text(), nullable=False),
        sa.Column("stripped_query", sa.Text(), nullable=False),
        sa.Column("context_string", sa.Text(), nullable=False),
        sa.Column("first_completion", sa.Text(), nullable=False),
        sa.Column("second_completion", sa.Text(), nullable=False),
        sa.Column("useful_urls_string", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=22), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("id", sa.String(length=22), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "conversations",
        sa.Column("user_id", sa.String(length=22), nullable=False),
        sa.Column("id", sa.String(length=22), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "nodes",
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("text_cleaned", sa.Text(), nullable=True),
        sa.Column("text_processed", sa.Text(), nullable=True),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(dim=1536), nullable=True),
        sa.Column("hash", sa.String(length=64), nullable=False),
        sa.Column("text_length", sa.Integer(), nullable=False),
        sa.Column("depth_level", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.String(length=22), nullable=True),
        sa.Column("document_id", sa.String(length=22), nullable=True),
        sa.Column("id", sa.String(length=22), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["nodes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hash"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "messages",
        sa.Column("conversation_id", sa.String(length=22), nullable=False),
        sa.Column("sender", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=22), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("messages")
    op.drop_table("nodes")
    op.drop_table("conversations")
    op.drop_table("users")
    op.drop_table("questions")
    op.drop_table("documents")
    # ### end Alembic commands ###
