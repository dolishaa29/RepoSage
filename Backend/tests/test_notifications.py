from app.core.auth import create_token
from app.services.notification_service import add_notification


def test_needs_login(client):
    assert client.get("/notifications").status_code == 401
    assert client.get("/notifications/unread").status_code == 401
    assert client.post("/notifications/read").status_code == 401


def test_count_list_and_read(client, db, user, headers):
    add_notification(db, user.id, "review", "first", "o/r")
    add_notification(db, user.id, "fix", "second", "o/r")
    db.commit()

    assert client.get("/notifications/unread", headers=headers).json() == {"count": 2}
    rows = client.get("/notifications", headers=headers).json()
    assert [row["message"] for row in rows] == ["second", "first"]
    assert rows[0]["link"] == "/repo/o/r" and rows[0]["is_read"] is False

    assert client.post("/notifications/read", headers=headers).status_code == 200
    assert client.get("/notifications/unread", headers=headers).json() == {"count": 0}


def test_other_user_is_separate(client, db, user, headers, make_user):
    other = make_user()
    other_headers = {"Authorization": f"Bearer {create_token(other.id)}"}
    add_notification(db, other.id, "fix", "not yours", "o/r")
    db.commit()

    assert client.get("/notifications", headers=headers).json() == []
    client.post("/notifications/read", headers=headers)
    assert client.get("/notifications/unread", headers=other_headers).json() == {"count": 1}
