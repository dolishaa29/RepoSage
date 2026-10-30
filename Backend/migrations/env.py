from alembic import context

from app.core.db import Base, engine
from app.models import code_chunk, fix, github_account, job, notification, review, seen_item, user

target_metadata = Base.metadata

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
