import hashlib
import hmac
import json
from unittest.mock import patch

from fastapi import HTTPException

from app.models.fix import Fix
from app.services import sync_service
from app.services.fix import fix_service

SECRET = "test-webhook-secret"


def pr(number, ref="feature"):
    return {"id": 900000 + number, "number": number, "title": f"PR{number}", "head": {"ref": ref}}


def repo_item(number, open_count=0):
    return {"id": 800000 + number, "full_name": f"o/r{number}", "open_issues_count": open_count}


def run_sync(db, user, repos, pulls=()):
    calls = []

    def fake_call(token, path):
        calls.append(path)
        return list(pulls)

    with patch.object(sync_service, "get_account_repos", lambda token: list(repos)), patch.object(sync_service, "call_github", fake_call):
        sync_service.sync_user(db, user)
    return calls


def test_first_sync_is_silent_then_only_new_items(db, user, account, notes):
    repos = [repo_item(1, 1), repo_item(2)]
    calls = run_sync(db, user, repos, [pr(1)])
    assert notes() == []
    assert calls == ["/repos/o/r1/pulls?per_page=100"]

    repos.append(repo_item(3))
    run_sync(db, user, repos, [pr(1), pr(2)])
    run_sync(db, user, repos, [pr(1), pr(2)])
    assert sorted(notes()) == ["New PR in o/r1 #2: PR2", "New repo: o/r3"]


def test_sync_skips_gitaudit_fix_prs(db, user, account, notes):
    repos = [repo_item(1, 1)]
    run_sync(db, user, repos, [])
    run_sync(db, user, repos, [pr(5, "gitaudit/fix-pr1-1")])
    assert notes() == []


def test_expired_token_does_not_stop_sync(db, user, account):
    with patch.object(sync_service, "get_account_repos", side_effect=HTTPException(400, "expired")):
        sync_service.sync_user(db, user)


def post_hook(client, event, data, secret=SECRET):
    body = json.dumps(data).encode()
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post("/webhooks/github", content=body, headers={"X-Hub-Signature-256": signature, "X-GitHub-Event": event})


def repo_payload(account):
    return {"id": 700001, "full_name": f"{account.username}/d", "owner": {"login": account.username}}


def test_webhook_refuses_bad_signature(client):
    assert client.post("/webhooks/github", content=b"{}").status_code == 401
    assert post_hook(client, "repository", {}, "wrong-secret").status_code == 401


def test_webhook_without_secret_setting(client, monkeypatch):
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET")
    assert client.post("/webhooks/github", content=b"{}").status_code == 503


def test_webhook_new_repo_and_pr_only_once(client, account, notes):
    repo = repo_payload(account)
    sender = {"login": "someone"}
    for _ in range(2):
        assert post_hook(client, "repository", {"action": "created", "repository": repo, "sender": sender}).status_code == 200
        assert post_hook(client, "pull_request", {"action": "opened", "repository": repo, "sender": sender, "pull_request": pr(7)}).status_code == 200
    assert notes() == [f"New repo: {repo['full_name']}", f"New PR in {repo['full_name']} #7: PR7"]


def test_webhook_ignores_other_events_and_strangers(client, account, notes):
    repo = repo_payload(account)
    stranger = {"id": 1, "full_name": "x/y", "owner": {"login": "stranger"}}
    assert post_hook(client, "ping", {"zen": "hi"}).status_code == 200
    assert post_hook(client, "pull_request", {"action": "closed", "repository": repo, "sender": {"login": "s"}, "pull_request": pr(8)}).status_code == 200
    assert post_hook(client, "pull_request", {"action": "opened", "repository": stranger, "sender": {"login": "s"}, "pull_request": pr(9)}).status_code == 200
    assert notes() == []


def make_running_fix(db, user, repo="o/r", attempts=1):
    fix = Fix(user_id=user.id, repo=repo, pr_number=1, file="a.py", title="t", explanation="e", changes=[], test_file="t.py",
              test_command="pytest", status="approved", branch="gitaudit/fix-1", ci_status="running", attempts=attempts)
    db.add(fix)
    db.commit()
    return fix.id


def completed_run(conclusion):
    return {"status": "completed", "conclusion": conclusion, "id": 1}


def test_workflow_run_webhook_updates_the_fix(client, db, user, account, notes):
    repo = repo_payload(account)
    fix_id = make_running_fix(db, user, repo["full_name"])
    with patch.object(fix_service, "get_token", return_value="x"), patch.object(fix_service, "latest_run", return_value=completed_run("success")):
        response = post_hook(client, "workflow_run", {"action": "completed", "repository": repo, "workflow_run": {"head_branch": "gitaudit/fix-1"}})
    assert response.status_code == 200
    db.expire_all()
    assert db.get(Fix, fix_id).ci_status == "passed"
    assert notes()[-1].startswith("Tests passed")


def test_broken_retry_stops_after_the_limit(db, user, notes):
    fix_id = make_running_fix(db, user)
    with patch.object(fix_service, "get_token", return_value="x"), \
            patch.object(fix_service, "latest_run", return_value=completed_run("failure")), \
            patch.object(fix_service, "test_log", return_value="log"), \
            patch.object(fix_service, "retry_fix", side_effect=HTTPException(502, "AI down")) as retry:
        for _ in range(5):
            sync_service.check_fix(db, user, fix_id)
    db.expire_all()
    assert retry.call_count == 2
    assert db.get(Fix, fix_id).ci_status == "failed"
    assert notes()[-1].startswith("Tests failed")


def test_cron_needs_the_secret(client):
    assert client.post("/internal/sync").status_code == 401
    assert client.post("/internal/sync", headers={"X-Cron-Secret": "bad"}).status_code == 401
    with patch.object(sync_service, "sync_all") as sync_all:
        assert client.post("/internal/sync", headers={"X-Cron-Secret": "test-cron-secret"}).status_code == 202
    sync_all.assert_called_once()
