from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi import HTTPException

from app.core.auth import create_token
from app.models.job import Job
from app.models.review import Review
from app.services.agent import code_index
from app.services.review import review_service

BODY = {"repo": "o/r", "pr_number": 5}


def fake_review(db, user, repo, pr_number):
    review = Review(user_id=user.id, repo=repo, pr_number=pr_number, pr_title="T", summary="S", findings=[], risk="low", pr_summary="P")
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def start_review(client, headers, **patch_args):
    with patch.object(review_service, "review_pr", **patch_args):
        return client.post("/reviews", json=BODY, headers=headers).json()


def test_review_job_finishes_with_the_review(client, headers):
    answer = start_review(client, headers, side_effect=fake_review)
    job = client.get(f"/jobs/{answer['job_id']}", headers=headers).json()
    assert job["status"] == "done"
    assert job["result"]["risk"] == "low" and job["result"]["pr_summary"] == "P"


def test_failed_job_shows_the_reason_and_notifies(client, headers, notes):
    answer = start_review(client, headers, side_effect=HTTPException(502, "AI review failed: boom"))
    job = client.get(f"/jobs/{answer['job_id']}", headers=headers).json()
    assert job["status"] == "failed" and "boom" in job["error"]
    assert notes()[-1].startswith("Review failed in o/r")


def test_unknown_crash_does_not_leak_details(client, headers):
    answer = start_review(client, headers, side_effect=RuntimeError("secret detail"))
    job = client.get(f"/jobs/{answer['job_id']}", headers=headers).json()
    assert job["status"] == "failed" and "secret" not in job["error"]


def test_index_job_returns_chunks(client, headers):
    with patch.object(code_index, "index_repo", return_value=12):
        answer = client.post("/github/repos/o/r/index", headers=headers).json()
    assert client.get(f"/jobs/{answer['job_id']}", headers=headers).json()["result"] == {"chunks": 12}


def test_job_is_private(client, headers, make_user):
    answer = start_review(client, headers, side_effect=fake_review)
    other = {"Authorization": f"Bearer {create_token(make_user().id)}"}
    assert client.get(f"/jobs/{answer['job_id']}", headers=other).status_code == 404
    assert client.get(f"/jobs/{answer['job_id']}").status_code == 401


def test_old_running_job_becomes_failed(client, db, user, headers):
    job = Job(user_id=user.id, kind="Review", created_at=datetime.now(timezone.utc) - timedelta(hours=1))
    db.add(job)
    db.commit()
    assert client.get(f"/jobs/{job.id}", headers=headers).json()["status"] == "failed"


def test_new_running_job_stays_running(client, db, user, headers):
    job = Job(user_id=user.id, kind="Review")
    db.add(job)
    db.commit()
    assert client.get(f"/jobs/{job.id}", headers=headers).json()["status"] == "running"
