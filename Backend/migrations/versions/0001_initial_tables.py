import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String, nullable=True),
        sa.Column("github_id", sa.BigInteger, nullable=True, unique=True),
        sa.Column("github_username", sa.String, nullable=True),
        sa.Column("github_token", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("repo", sa.String, nullable=False),
        sa.Column("pr_number", sa.Integer, nullable=False),
        sa.Column("pr_title", sa.String, nullable=False),
        sa.Column("ai", sa.String, nullable=True),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("findings", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "fixes",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("repo", sa.String, nullable=False),
        sa.Column("pr_number", sa.Integer, nullable=False),
        sa.Column("file", sa.String, nullable=False),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("explanation", sa.Text, nullable=False),
        sa.Column("old_code", sa.Text, nullable=False),
        sa.Column("new_code", sa.Text, nullable=False),
        sa.Column("test_file", sa.String, nullable=False),
        sa.Column("test_code", sa.Text, nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("pr_url", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("branch", sa.String, nullable=True),
        sa.Column("ci_status", sa.String, nullable=True),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("test_command", sa.Text, nullable=False, server_default=""),
    )


def downgrade():
    op.drop_table("fixes")
    op.drop_table("reviews")
    op.drop_table("users")
