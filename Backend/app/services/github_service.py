import os
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..core.auth import create_token
from ..models.github_account import GithubAccount
from ..models.user import User

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")


def login(db: Session, code: str):
    token = get_github_token(code)
    github_user = call_github(token, "/user")

    account = find_account(db, github_user["id"])
    if account is None:
        email = get_email(token)
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Email already registered. Log in with your password, then connect GitHub")
        user = User(name=github_user["name"] or github_user["login"], email=email)
        db.add(user)
        db.flush()
        user_id = user.id
    else:
        user_id = account.user_id

    save_account(db, user_id, github_user, token)
    db.commit()
    return create_token(user_id)


def connect(db: Session, user: User, code: str):
    token = get_github_token(code)
    github_user = call_github(token, "/user")

    account = find_account(db, github_user["id"])
    if account and account.user_id != user.id:
        raise HTTPException(status_code=400, detail="This GitHub account is linked to another user")

    save_account(db, user.id, github_user, token)
    db.commit()
    db.refresh(user)
    return user


def remove_account(db: Session, user: User, account_id: int):
    account = db.query(GithubAccount).filter(GithubAccount.id == account_id, GithubAccount.user_id == user.id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="GitHub account not found")
    db.delete(account)
    db.commit()
    db.refresh(user)
    return user


def get_repos(user: User):
    if len(user.github_accounts) == 0:
        raise HTTPException(status_code=400, detail="Connect GitHub first")

    result = []
    seen = set()
    for account in user.github_accounts:
        repos = call_github(account.token, "/user/repos?sort=updated&per_page=100")
        for repo in repos:
            if repo["id"] in seen:
                continue
            seen.add(repo["id"])
            repo["account"] = account.username
            result.append(repo)

    result.sort(key=lambda repo: repo["updated_at"], reverse=True)
    return result


def get_pulls(user: User, repo: str):
    token = get_token(user, repo)
    pulls = call_github(token, f"/repos/{repo}/pulls")
    result = []
    for p in pulls:
        pull = {
            "number": p["number"],
            "title": p["title"],
            "author": p["user"]["login"],
            "html_url": p["html_url"],
        }
        result.append(pull)
    return result


# picks the linked account that can open this repo
def get_token(user: User, repo: str):
    if len(user.github_accounts) == 0:
        raise HTTPException(status_code=400, detail="Connect GitHub first")

    owner = repo.split("/")[0].lower()
    for account in user.github_accounts:
        if account.username.lower() == owner:
            return account.token

    for account in user.github_accounts:
        res = httpx.get(f"https://api.github.com/repos/{repo}", headers={"Authorization": f"Bearer {account.token}"})
        if res.status_code == 200:
            return account.token

    raise HTTPException(status_code=400, detail="None of your GitHub accounts can open this repo")


def find_account(db: Session, github_id: int):
    return db.query(GithubAccount).filter(GithubAccount.github_id == github_id).first()


def save_account(db: Session, user_id: int, github_user: dict, token: str):
    account = find_account(db, github_user["id"])
    if account is None:
        account = GithubAccount(user_id=user_id, github_id=github_user["id"])
        db.add(account)
    account.username = github_user["login"]
    account.token = token


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


def get_github_text(token: str, path: str):
    res = httpx.get("https://api.github.com" + path, headers={"Authorization": f"Bearer {token}"}, follow_redirects=True)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not read the test log from GitHub")
    return res.text


def send_github(token: str, method: str, path: str, body: dict):
    res = httpx.request(method, "https://api.github.com" + path, json=body, headers={"Authorization": f"Bearer {token}"})
    if res.status_code not in (200, 201):
        raise HTTPException(status_code=400, detail=f"GitHub request failed: {res.json().get('message')}")
    return res.json()


def get_raw_file(token: str, repo: str, path: str, ref: str):
    res = httpx.get(
        f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.raw"},
        follow_redirects=True,
    )
    if res.status_code == 404:
        return None
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="GitHub request failed, connect GitHub again")
    return res.text


def search_github_code(token: str, repo: str, text: str):
    res = httpx.get(
        "https://api.github.com/search/code",
        params={"q": f"{text} repo:{repo}", "per_page": 10},
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.text-match+json"},
    )
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="GitHub code search failed")
    return res.json()["items"]


def get_github_bytes(token: str, path: str, max_size: int):
    data = bytearray()
    with httpx.stream("GET", "https://api.github.com" + path, headers={"Authorization": f"Bearer {token}"}, follow_redirects=True, timeout=60) as res:
        if res.status_code != 200:
            raise HTTPException(status_code=400, detail="GitHub download failed, connect GitHub again")
        for part in res.iter_bytes():
            data.extend(part)
            if len(data) > max_size:
                raise HTTPException(status_code=400, detail="This repo is too big to index")
    return bytes(data)
