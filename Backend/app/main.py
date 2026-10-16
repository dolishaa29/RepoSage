from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.db import Base, engine
from .models import user  
from .routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
