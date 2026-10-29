import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    # old github_accounts table allowed only one account per user
    op.drop_constraint("github_accounts_user_id_key", "github_accounts", type_="unique")
    op.create_index("ix_github_accounts_user_id", "github_accounts", ["user_id"])

    # move the GitHub account saved on users into github_accounts (token is already encrypted)
    op.execute("DELETE FROM github_accounts")
    op.execute("""
        INSERT INTO github_accounts (user_id, github_id, username, encrypted_token)
        SELECT id, github_id, github_username, github_token FROM users
        WHERE github_id IS NOT NULL AND github_token IS NOT NULL
    """)

    op.drop_column("users", "github_id")
    op.drop_column("users", "github_username")
    op.drop_column("users", "github_token")


def downgrade():
    op.add_column("users", sa.Column("github_id", sa.BigInteger, nullable=True))
    op.add_column("users", sa.Column("github_username", sa.String, nullable=True))
    op.add_column("users", sa.Column("github_token", sa.String, nullable=True))

    # users can hold only one account again, keep the first one
    op.execute("""
        UPDATE users SET github_id = g.github_id, github_username = g.username, github_token = g.encrypted_token
        FROM (SELECT DISTINCT ON (user_id) * FROM github_accounts ORDER BY user_id, id) g
        WHERE users.id = g.user_id
    """)
    op.execute("DELETE FROM github_accounts WHERE id NOT IN (SELECT MIN(id) FROM github_accounts GROUP BY user_id)")

    op.drop_index("ix_github_accounts_user_id", "github_accounts")
    op.create_unique_constraint("github_accounts_user_id_key", "github_accounts", ["user_id"])
