import sqlalchemy as sa
from alembic import op
from cryptography.fernet import InvalidToken

from app.core.crypto import decrypt, encrypt

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    db = op.get_bind()
    users = db.execute(sa.text("SELECT id, github_token FROM users WHERE github_token IS NOT NULL")).fetchall()
    for user_id, token in users:
        if is_encrypted(token):
            continue
        db.execute(sa.text("UPDATE users SET github_token = :t WHERE id = :id"), {"t": encrypt(token), "id": user_id})


def downgrade():
    db = op.get_bind()
    users = db.execute(sa.text("SELECT id, github_token FROM users WHERE github_token IS NOT NULL")).fetchall()
    for user_id, token in users:
        if is_encrypted(token):
            db.execute(sa.text("UPDATE users SET github_token = :t WHERE id = :id"), {"t": decrypt(token), "id": user_id})


def is_encrypted(token: str):
    try:
        decrypt(token)
        return True
    except InvalidToken:
        return False
