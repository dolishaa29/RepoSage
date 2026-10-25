from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import fix, github, review, user


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(github.router)
app.include_router(review.router)
app.include_router(fix.router)
