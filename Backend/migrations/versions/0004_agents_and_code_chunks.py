import json

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "code_chunks",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("repo", sa.String, nullable=False, index=True),
        sa.Column("path", sa.String, nullable=False),
        sa.Column("start_line", sa.Integer, nullable=False),
        sa.Column("end_line", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding", Vector(768), nullable=False),
    )

    op.add_column("fixes", sa.Column("changes", sa.JSON, nullable=False, server_default="[]"))
    conn = op.get_bind()
    for fix in conn.execute(sa.text("SELECT id, file, old_code, new_code, test_file, test_code FROM fixes")):
        changes = [{"file": fix.file, "old_code": fix.old_code, "new_code": fix.new_code}]
        if fix.test_file:
            changes.append({"file": fix.test_file, "old_code": "", "new_code": fix.test_code})
        conn.execute(sa.text("UPDATE fixes SET changes = CAST(:changes AS json) WHERE id = :id"), {"changes": json.dumps(changes), "id": fix.id})
    op.drop_column("fixes", "old_code")
    op.drop_column("fixes", "new_code")
    op.drop_column("fixes", "test_code")


def downgrade():
    op.add_column("fixes", sa.Column("old_code", sa.Text, nullable=False, server_default=""))
    op.add_column("fixes", sa.Column("new_code", sa.Text, nullable=False, server_default=""))
    op.add_column("fixes", sa.Column("test_code", sa.Text, nullable=False, server_default=""))
    conn = op.get_bind()
    for fix in conn.execute(sa.text("SELECT id, file, test_file, changes FROM fixes")):
        changes = {change["file"]: change for change in fix.changes}
        main = changes.get(fix.file, {"old_code": "", "new_code": ""})
        test = changes.get(fix.test_file, {"new_code": ""})
        conn.execute(
            sa.text("UPDATE fixes SET old_code = :old, new_code = :new, test_code = :test WHERE id = :id"),
            {"old": main["old_code"], "new": main["new_code"], "test": test["new_code"], "id": fix.id},
        )
    op.drop_column("fixes", "changes")
    op.drop_table("code_chunks")
