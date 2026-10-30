from types import SimpleNamespace
from unittest.mock import patch

from app.schemas.review import ReviewResult
from app.services.review import review_service as rs


def fake_github(token, path):
    if path.endswith("/files?per_page=100"):
        return [{"filename": "a.py", "patch": "+x", "additions": 1, "deletions": 0}]
    return {"title": "T", "changed_files": 1, "head": {"sha": "abc"}}


def test_review_saves_risk_summary_and_notification(db, user, notes):
    result = ReviewResult(summary="S", risk="high", what_changed="Changed X", what_to_test="Test Y", findings=[])
    with patch.object(rs, "get_token", return_value="t"), patch.object(rs, "call_github", fake_github), \
            patch.object(rs.review_graph, "invoke", return_value={"result": result}):
        review = rs.review_pr(db, user, "o/r", 3)
    assert review.risk == "high"
    assert review.pr_summary == "### What changed\nChanged X\n\n### What to test\nTest Y"
    assert notes() == ["Review ready for o/r #3: 0 findings"]


def test_summary_is_added_to_an_empty_body():
    body = rs.add_summary_to_body("", "S1")
    assert body.startswith(rs.SUMMARY_START) and "S1" in body


def test_summary_keeps_the_users_text_and_replaces_only_its_part():
    first = rs.add_summary_to_body("my text", "S1")
    second = rs.add_summary_to_body(first + "\n\nadded later", "S2")
    assert "S1" not in second and "S2" in second
    assert "my text" in second and "added later" in second
    assert second.count(rs.SUMMARY_START) == 1


def test_publish_sends_a_patch_to_github(client, db, user, headers):
    review = rs.Review(user_id=user.id, repo="o/r", pr_number=2, pr_title="T", summary="S", findings=[], pr_summary="P")
    db.add(review)
    db.commit()
    sent = {}
    with patch.object(rs, "get_token", return_value="t"), patch.object(rs, "call_github", return_value={"body": None}), \
            patch.object(rs, "send_github", lambda token, method, path, body: sent.update(method=method, path=path, body=body)):
        assert client.post(f"/reviews/{review.id}/publish-summary", headers=headers).status_code == 200
    assert sent["method"] == "PATCH" and sent["path"] == "/repos/o/r/pulls/2" and "P" in sent["body"]["body"]


def test_publish_is_private(client, db, user, headers, make_user):
    other = make_user()
    review = rs.Review(user_id=other.id, repo="o/r", pr_number=2, pr_title="T", summary="S", findings=[], pr_summary="P")
    db.add(review)
    db.commit()
    assert client.post(f"/reviews/{review.id}/publish-summary", headers=headers).status_code == 404


def test_old_review_without_summary_cannot_be_published(client, db, user, headers):
    review = rs.Review(user_id=user.id, repo="o/r", pr_number=2, pr_title="T", summary="S", findings=[])
    db.add(review)
    db.commit()
    assert client.post(f"/reviews/{review.id}/publish-summary", headers=headers).status_code == 400


def test_big_pr_says_some_files_were_skipped():
    files = [{"filename": "a.py", "patch": "+x"}, {"filename": "package-lock.json", "patch": "+y"}]
    chunks, skipped = rs.make_chunks(files)
    assert len(chunks) == 1 and skipped == ["package-lock.json"]
