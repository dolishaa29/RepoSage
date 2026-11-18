import json

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..services import webhook_service

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

