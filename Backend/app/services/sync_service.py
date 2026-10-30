import time

from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..core.db import SessionLocal
from ..models.fix import Fix
from ..models.seen_item import SeenItem
from ..models.user import User
from .fix import fix_service
from .github_service import call_github, get_account_repos
from .notification_service import add_notification

FIX_BRANCH = "gitaudit/"


def mark_seen(db: Session, user_id: int, key: str):
    query = insert(SeenItem).values(user_id=user_id, key=key).on_conflict_do_nothing().returning(SeenItem.id)
    return db.execute(query).first() is not None


def notify_new_repo(db: Session, user_id: int, repo_id: int, repo: str):
    if mark_seen(db, user_id, f"repo:{repo_id}"):
        add_notification(db, user_id, "new_repo", f"New repo: {repo}", repo)


def notify_new_pr(db: Session, user_id: int, pr: dict, repo: str):
    if pr["head"]["ref"].startswith(FIX_BRANCH):
        return
    if mark_seen(db, user_id, f"pr:{pr['id']}"):
        add_notification(db, user_id, "new_pr", f"New PR in {repo} #{pr['number']}: {pr['title']}", repo)


def sync_account(db: Session, user_id: int, account):
    is_first_sync = mark_seen(db, user_id, f"account:{account.id}")

    for repo in get_account_repos(account.token):
        if is_first_sync:
            mark_seen(db, user_id, f"repo:{repo['id']}")
        else:
            notify_new_repo(db, user_id, repo["id"], repo["full_name"])

        if repo["open_issues_count"] == 0:
            continue

        pulls = call_github(account.token, f"/repos/{repo['full_name']}/pulls?per_page=100")
        for pr in pulls:
            if is_first_sync:
                mark_seen(db, user_id, f"pr:{pr['id']}")
            else:
                notify_new_pr(db, user_id, pr, repo["full_name"])
    db.commit()


def check_fix(db: Session, user: User, fix_id: int):
    try:
        fix_service.check_tests(db, user, fix_id)
    except Exception:
        db.rollback()
        fix = db.get(Fix, fix_id)
        fix.attempts += 1
        db.commit()


def check_fix_by_id(fix_id: int, user_id: int):
    db = SessionLocal()
    try:
        check_fix(db, db.get(User, user_id), fix_id)
    finally:
        db.close()


def sync_user(db: Session, user: User):
    for account in user.github_accounts:
        try:
            sync_account(db, user.id, account)
        except HTTPException:
            db.rollback()

    running = db.query(Fix.id).filter(Fix.user_id == user.id, Fix.ci_status == "running").all()
    for row in running:
        check_fix(db, user, row.id)


def sync_all():
    db = SessionLocal()
    try:
        user_ids = [row.id for row in db.query(User.id).all()]
        for user_id in user_ids:
            sync_user(db, db.get(User, user_id))
    finally:
        db.close()


def sync_forever(minutes: int):
    while True:
        try:
            sync_all()
        except Exception:
            pass
        time.sleep(minutes * 60)
