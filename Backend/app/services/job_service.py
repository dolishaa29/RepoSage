from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from ..core.db import SessionLocal
from ..models.job import Job
from ..models.user import User
from .notification_service import add_notification

MAX_JOB_TIME = timedelta(minutes=45)
MAX_ERROR_IN_NOTIFICATION = 200


def start_job(db: Session, user: User, background: BackgroundTasks, kind: str, repo: str, work):
    job = Job(user_id=user.id, kind=kind)
    db.add(job)
    db.commit()
    background.add_task(run_job, job.id, user.id, kind, repo, work)
    return to_response(job)


def run_job(job_id: int, user_id: int, kind: str, repo: str, work):
    db = SessionLocal()
    try:
        try:
            result = work(db, db.get(User, user_id))
            status = "done"
            error = None
        except HTTPException as e:
            db.rollback()
            result = None
            status = "failed"
            error = str(e.detail)
        except Exception:
            db.rollback()
            result = None
            status = "failed"
            error = f"The {kind} job failed, please try again"

        job = db.get(Job, job_id)
        job.status = status
        job.result = result
        job.error = error
        if status == "failed":
            add_notification(db, user_id, "job_failed", f"{kind} failed in {repo}: {error[:MAX_ERROR_IN_NOTIFICATION]}", repo)
        db.commit()
    finally:
        db.close()


def get_job(db: Session, user: User, job_id: int):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == "running" and datetime.now(timezone.utc) - job.created_at > MAX_JOB_TIME:
        job.status = "failed"
        job.error = "This job stopped, please try again"
        db.commit()
    return to_response(job)


def to_response(job: Job):
    return {"job_id": job.id, "status": job.status, "result": job.result, "error": job.error}
