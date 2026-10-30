import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    # old reviews keep these empty
    op.add_column("reviews", sa.Column("risk", sa.String, nullable=True))
    op.add_column("reviews", sa.Column("pr_summary", sa.Text, nullable=True))


def downgrade():
    op.drop_column("reviews", "pr_summary")
    op.drop_column("reviews", "risk")
