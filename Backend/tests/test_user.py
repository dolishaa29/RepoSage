import pytest


@pytest.mark.parametrize("path", ["/register", "/login", "/forgot-password", "/reset-password"])
def test_password_endpoints_are_removed(client, path):
    assert client.post(path, json={}).status_code == 404


def test_me_requires_valid_auth(client):
    assert client.get("/me").status_code == 401
    assert client.get("/me", headers={"Authorization": "Bearer bad"}).status_code == 401


def test_health_check(client):
    assert client.get("/health").json() == {"status": "ok"}
