from alembic import context

from app.core.db import Base, engine
from app.models import fix, review, user  # importing the models registers their tables on Base.metadata

# Alembic compares the models (Base.metadata) with the database to write new migrations.
# It uses our own engine from core/db.py, so it reads DATABASE_URL from .env and gets the same IPv4 fix.
target_metadata = Base.metadata

# old tables from earlier versions of the project (github_accounts, audits) are still in the database.
# Alembic only looks at tables we have models for, so it never offers to drop them by mistake.
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and reflected and compare_to is None:
        return False
    return True


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, include_object=include_object)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
