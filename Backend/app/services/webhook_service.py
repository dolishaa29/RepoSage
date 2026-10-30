import hashlib
import hmac
import os

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.fix import Fix
from ..models.github_account import GithubAccount
from .sync_service import FIX_BRANCH, check_fix_by_id, notify_new_pr, notify_new_repo


def check_signature(body: bytes, signature: str | None):
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="GITHUB_WEBHOOK_SECRET is not set")

    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if signature is None or not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")


def find_user_ids(db: Session, logins: list[str]):
    names = [login.lower() for login in logins]
    accounts = db.query(GithubAccount).filter(func.lower(GithubAccount.username).in_(names)).all()
    return {account.user_id for account in accounts}


def handle_event(db: Session, background: BackgroundTasks, event: str, data: dict):
    action = data.get("action")
    if event == "pull_request" and action == "opened":
        handle_new_pr(db, data)
    elif event == "repository" and action == "created":
        handle_new_repo(db, data)
    elif event == "installation_repositories" and action == "added":
        handle_added_repos(db, data)
    elif event == "workflow_run" and action == "completed":
        handle_test_run(db, background, data)
    db.commit()


def handle_new_pr(db: Session, data: dict):
    repo = data["repository"]
    for user_id in find_user_ids(db, [repo["owner"]["login"], data["sender"]["login"]]):
        notify_new_pr(db, user_id, data["pull_request"], repo["full_name"])


def handle_new_repo(db: Session, data: dict):
    repo = data["repository"]
    for user_id in find_user_ids(db, [repo["owner"]["login"], data["sender"]["login"]]):
        notify_new_repo(db, user_id, repo["id"], repo["full_name"])


def handle_added_repos(db: Session, data: dict):
    for user_id in find_user_ids(db, [data["installation"]["account"]["login"], data["sender"]["login"]]):
        for repo in data["repositories_added"]:
            notify_new_repo(db, user_id, repo["id"], repo["full_name"])


def handle_test_run(db: Session, background: BackgroundTasks, data: dict):
    branch = data["workflow_run"]["head_branch"]
    if not branch or not branch.startswith(FIX_BRANCH):
        return

    repo = data["repository"]["full_name"]
    fixes = db.query(Fix).filter(Fix.repo == repo, Fix.branch == branch, Fix.ci_status == "running").all()
    for fix in fixes:
        background.add_task(check_fix_by_id, fix.id, fix.user_id)
