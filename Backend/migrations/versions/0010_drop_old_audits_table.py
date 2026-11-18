from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


# The audits table was used by the old Bandit audit feature, which was removed.
def upgrade():
    op.execute("DROP TABLE IF EXISTS audits")


def downgrade():
    pass
