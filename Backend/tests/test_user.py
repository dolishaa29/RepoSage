import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.models.password_reset import PasswordReset
from app.models.user import User
from app.services import email_service, user_service


def new_email():
    return f"pytest-{uuid.uuid4().hex}@example.com"


def register(client, email, password="secret1"):
    return client.post("/register", json={"name": "Test", "email": email, "password": password})


def test_register_and_login_ignore_email_case(client):
    email = new_email()
    assert register(client, email.upper()).status_code == 200
    assert client.post("/login", json={"email": email, "password": "secret1"}).status_code == 200
    assert register(client, email).status_code == 400


def test_short_password_is_refused(client):
    assert register(client, new_email(), "123").status_code == 422


def test_wrong_password_is_refused(client):
    email = new_email()
    register(client, email)
    assert client.post("/login", json={"email": email, "password": "wrong-one"}).status_code == 401


def test_me_needs_login(client):
    assert client.get("/me").status_code == 401
    assert client.get("/me", headers={"Authorization": "Bearer bad"}).status_code == 401


def forgot(client, email):
    sent = []
    with patch.object(email_service, "is_configured", return_value=True), \
            patch.object(email_service, "send_email", lambda to, subject, text: sent.append((to, text))):
        response = client.post("/forgot-password", json={"email": email})
    return response, sent


def token_from(sent):
    return sent[0][1].split("token=")[1].split()[0]


def test_reset_password_works_only_once(client):
    email = new_email()
    register(client, email)
    response, sent = forgot(client, email)
    assert response.status_code == 200 and sent[0][0] == email
    token = token_from(sent)

    assert client.post("/reset-password", json={"token": token, "password": "newpass1"}).status_code == 200
    assert client.post("/login", json={"email": email, "password": "newpass1"}).status_code == 200
    assert client.post("/login", json={"email": email, "password": "secret1"}).status_code == 401
    assert client.post("/reset-password", json={"token": token, "password": "another1"}).status_code == 400


def test_unknown_email_gets_same_answer_and_no_mail(client):
    response, sent = forgot(client, new_email())
    assert response.status_code == 200 and sent == []


def test_new_link_cancels_the_old_one(client):
    email = new_email()
    register(client, email)
    _, first = forgot(client, email)
    _, second = forgot(client, email)
    assert client.post("/reset-password", json={"token": token_from(first), "password": "newpass1"}).status_code == 400
    assert client.post("/reset-password", json={"token": token_from(second), "password": "newpass1"}).status_code == 200


def test_expired_link_is_refused(client, db):
    email = new_email()
    register(client, email)
    _, sent = forgot(client, email)
    token = token_from(sent)
    reset = db.query(PasswordReset).filter(PasswordReset.token_hash == user_service.hash_reset_token(token)).one()
    reset.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()
    assert client.post("/reset-password", json={"token": token, "password": "newpass1"}).status_code == 400


def test_token_is_not_saved_as_plain_text(client, db):
    email = new_email()
    register(client, email)
    _, sent = forgot(client, email)
    user = db.query(User).filter(User.email == email).one()
    reset = db.query(PasswordReset).filter(PasswordReset.user_id == user.id).one()
    assert reset.token_hash != token_from(sent)


def test_forgot_password_without_email_settings(client, monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    assert client.post("/forgot-password", json={"email": new_email()}).status_code == 503
