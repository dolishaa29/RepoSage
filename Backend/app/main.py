import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import fix, github, job, notification, review, stats, user, webhook
from .services.sync_service import sync_forever

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5174")
SYNC_EVERY_MINUTES = int(os.getenv("SYNC_EVERY_MINUTES", "3"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    if SYNC_EVERY_MINUTES > 0:
        threading.Thread(target=sync_forever, args=(SYNC_EVERY_MINUTES,), daemon=True).start()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(github.router)
app.include_router(review.router)
app.include_router(fix.router)
app.include_router(stats.router)
app.include_router(notification.router)
app.include_router(job.router)
app.include_router(webhook.router)
