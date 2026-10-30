import os
import uuid

os.environ["GITHUB_WEBHOOK_SECRET"] = "test-webhook-secret"
os.environ["CRON_SECRET"] = "test-cron-secret"
os.environ["SYNC_EVERY_MINUTES"] = "0"

import pytest
from fastapi.testclient import TestClient

from app.core.auth import create_token
from app.core.db import SessionLocal
from app.main import app
from app.models.fix import Fix
from app.models.github_account import GithubAccount
from app.models.job import Job
from app.models.notification import Notification
from app.models.password_reset import PasswordReset
from app.models.review import Review
from app.models.seen_item import SeenItem
from app.models.user import User

CHILD_TABLES = (Notification, PasswordReset, SeenItem, Job, Review, Fix, GithubAccount)


def remove_test_users():
    db = SessionLocal()
    test_users = db.query(User.id).filter(User.email.like("pytest-%@example.com"))
    user_ids = [row.id for row in test_users.all()]
    for model in CHILD_TABLES:
        db.query(model).filter(model.user_id.in_(user_ids)).delete(synchronize_session=False)
    db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
    db.commit()
    db.close()


@pytest.fixture(autouse=True)
def clean_up():
    yield
    remove_test_users()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def make_user(db):
    def make():
        user = User(name="Test", email=f"pytest-{uuid.uuid4().hex}@example.com")
        db.add(user)
        db.commit()
        return user
    return make


@pytest.fixture
def user(make_user):
    return make_user()


@pytest.fixture
def headers(user):
    return {"Authorization": f"Bearer {create_token(user.id)}"}


@pytest.fixture
def account(db, user):
    item = GithubAccount(user_id=user.id, github_id=uuid.uuid4().int % 10**15, username=f"pytest{user.id}", token="fake-token")
    db.add(item)
    db.commit()
    return item


@pytest.fixture
def notes(db, user):
    def read():
        db.expire_all()
        rows = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.id).all()
        return [row.message for row in rows]
    return read
