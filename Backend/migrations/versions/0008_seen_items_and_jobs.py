import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "seen_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("key", sa.String, nullable=False),
        sa.UniqueConstraint("user_id", "key", name="uq_seen_items_user_key"),
    )
    op.create_index("ix_seen_items_id", "seen_items", ["id"])

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("kind", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("result", sa.JSON, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_jobs_id", "jobs", ["id"])
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])


def downgrade():
    op.drop_index("ix_jobs_user_id", "jobs")
    op.drop_index("ix_jobs_id", "jobs")
    op.drop_table("jobs")
    op.drop_index("ix_seen_items_id", "seen_items")
    op.drop_table("seen_items")
