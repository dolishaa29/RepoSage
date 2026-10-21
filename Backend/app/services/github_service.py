import os
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..core.auth import create_token
from ..models.user import User

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")



def login(db: Session, code: str):
    token = get_github_token(code)
    github_user = call_github(token, "/user")

    user = db.query(User).filter(User.github_id == github_user["id"]).first()
    if user is None:
        email = get_email(token)
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Email already registered. Log in with your password, then connect GitHub")
        user = User(name=github_user["name"] or github_user["login"], email=email)
        db.add(user)

    save_github(user, github_user, token)
    db.commit()
    return create_token(user.id)


def connect(db: Session, user: User, code: str):
    token = get_github_token(code)
    github_user = call_github(token, "/user")

    other = db.query(User).filter(User.github_id == github_user["id"], User.id != user.id).first()
    if other:
        raise HTTPException(status_code=400, detail="This GitHub account is linked to another user")

    save_github(user, github_user, token)
    db.commit()
    db.refresh(user)
    return user



def get_repos(user: User):
    if user.github_token is None:
        raise HTTPException(status_code=400, detail="Connect GitHub first")
    return call_github(user.github_token, "/user/repos?sort=updated")  


def get_pulls(user: User, repo: str):
    if user.github_token is None:
        raise HTTPException(status_code=400, detail="Connect GitHub first")
    pulls = call_github(user.github_token, f"/repos/{repo}/pulls")
    return [
        {"number": p["number"], "title": p["title"], "author": p["user"]["login"], "html_url": p["html_url"]}
        for p in pulls
    ]


def save_github(user: User, github_user: dict, token: str):
    user.github_id = github_user["id"]
    user.github_username = github_user["login"]
    user.github_token = token


def get_github_token(code: str):
    res = httpx.post(
        "https://github.com/login/oauth/access_token",
        data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code},
        headers={"Accept": "application/json"},
    )
    token = res.json().get("access_token")
    if token is None:
        raise HTTPException(status_code=400, detail="GitHub login failed, please try again")
    return token


def get_email(token: str):
    emails = call_github(token, "/user/emails")
    for item in emails:
        if item["primary"]:
            return item["email"].lower()


def call_github(token: str, path: str):
    res = httpx.get("https://api.github.com" + path, headers={"Authorization": f"Bearer {token}"})
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="GitHub request failed, connect GitHub again")
    return res.json()


# CI logs are plain text, not JSON, and GitHub sends us to the log with a redirect,
# so this helper follows the redirect and returns the text
def get_github_text(token: str, path: str):
    res = httpx.get("https://api.github.com" + path, headers={"Authorization": f"Bearer {token}"}, follow_redirects=True)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not read the test log from GitHub")
    return res.text


# the file's current sha, or None if it does not exist yet. A missing file is normal here
# (a new test file), so 404 is not an error. call_github would raise on it.
def find_file_sha(token: str, repo: str, path: str, branch: str):
    res = httpx.get(f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}", headers={"Authorization": f"Bearer {token}"})
    if res.status_code == 404:
        return None
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="GitHub request failed, connect GitHub again")
    return res.json()["sha"]


# call_github only reads (GET). This one writes (POST / PUT): create a branch, commit a file, open a PR.
# GitHub's own error message is passed on, because it says exactly what went wrong (e.g. missing permission).
def send_github(token: str, method: str, path: str, body: dict):
    res = httpx.request(method, "https://api.github.com" + path, json=body, headers={"Authorization": f"Bearer {token}"})
    if res.status_code not in (200, 201):
        raise HTTPException(status_code=400, detail=f"GitHub request failed: {res.json().get('message')}")
    return res.json()
