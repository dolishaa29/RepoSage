import hmac
import json
import os

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..services import sync_service, webhook_service

router = APIRouter(tags=["Webhooks"])


async def read_body(request: Request):
    return await request.body()


@router.post("/webhooks/github")
def github_webhook(
    background: BackgroundTasks,
    body: bytes = Depends(read_body),
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str = Header(default=""),
    db: Session = Depends(get_db),
):
    webhook_service.check_signature(body, x_hub_signature_256)
    webhook_service.handle_event(db, background, x_github_event, json.loads(body))
    return {"ok": True}


# for a cron job on hosts where the server sleeps
@router.post("/internal/sync", status_code=202)
def run_sync(background: BackgroundTasks, x_cron_secret: str = Header(default="")):
    secret = os.getenv("CRON_SECRET")
    if not secret or not hmac.compare_digest(secret, x_cron_secret):
        raise HTTPException(status_code=401, detail="Invalid secret")
    background.add_task(sync_service.sync_all)
    return {"ok": True}
