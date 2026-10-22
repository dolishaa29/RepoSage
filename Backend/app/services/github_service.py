import os
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..core.auth import create_token
from ..models.user import User

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
print("github client id", CLIENT_ID)


def login(db: Session, code: str):
    print("github login", code)
    token = get_github_token(code)
    github_user = call_github(token, "/user")
    print("github user", github_user["id"], github_user["login"])

    user = db.query(User).filter(User.github_id == github_user["id"]).first()
    if user is None:
        print("new user")
        email = get_email(token)
        print("email", email)
        if db.query(User).filter(User.email == email).first():
            print("email exists", email)
            raise HTTPException(status_code=400, detail="Email already registered. Log in with your password, then connect GitHub")
        user = User(name=github_user["name"] or github_user["login"], email=email)
        db.add(user)
    else:
        print("old user", user.id)

    save_github(user, github_user, token)
    db.commit()
    print("user saved", user.id)
    return create_token(user.id)


def connect(db: Session, user: User, code: str):
    print("connecting", user.id, code)
    token = get_github_token(code)
    github_user = call_github(token, "/user")
    print("github user", github_user["id"], github_user["login"])

    other = db.query(User).filter(User.github_id == github_user["id"], User.id != user.id).first()
    if other:
        print("already linked", other.id)
        raise HTTPException(status_code=400, detail="This GitHub account is linked to another user")

    save_github(user, github_user, token)
    db.commit()
    db.refresh(user)
    print("connected", user.id)
    return user


def get_repos(user: User):
    print("getting repos", user.id)
    if user.github_token is None:
        print("no token")
        raise HTTPException(status_code=400, detail="Connect GitHub first")
    repos = call_github(user.github_token, "/user/repos?sort=updated")
    print("repos count", len(repos))
    return repos


def get_pulls(user: User, repo: str):
    print("getting pulls", repo)
    if user.github_token is None:
        print("no token")
        raise HTTPException(status_code=400, detail="Connect GitHub first")
    pulls = call_github(user.github_token, f"/repos/{repo}/pulls")
    print("pulls count", len(pulls))
    return [
        {"number": p["number"], "title": p["title"], "author": p["user"]["login"], "html_url": p["html_url"]}
        for p in pulls
    ]


def save_github(user: User, github_user: dict, token: str):
    print("saving github", github_user["id"], github_user["login"], token)
    user.github_id = github_user["id"]
    user.github_username = github_user["login"]
    user.github_token = token


def get_github_token(code: str):
    print("getting token", code)
    res = httpx.post(
        "https://github.com/login/oauth/access_token",
        data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code},
        headers={"Accept": "application/json"},
    )
    print("token response", res.status_code, res.json())
    token = res.json().get("access_token")
    if token is None:
        print("no token")
        raise HTTPException(status_code=400, detail="GitHub login failed, please try again")
    return token


def get_email(token: str):
    emails = call_github(token, "/user/emails")
    print("emails", emails)
    for item in emails:
        if item["primary"]:
            return item["email"].lower()


def call_github(token: str, path: str):
    print("github get", path)
    res = httpx.get("https://api.github.com" + path, headers={"Authorization": f"Bearer {token}"})
    print("status", res.status_code)
    if res.status_code != 200:
        print("github error", res.text)
        raise HTTPException(status_code=400, detail="GitHub request failed, connect GitHub again")
    return res.json()


def get_github_text(token: str, path: str):
    print("github text", path)
    res = httpx.get("https://api.github.com" + path, headers={"Authorization": f"Bearer {token}"}, follow_redirects=True)
    print("status", res.status_code)
    if res.status_code != 200:
        print("github error", res.text)
        raise HTTPException(status_code=400, detail="Could not read the test log from GitHub")
    return res.text


def find_file_sha(token: str, repo: str, path: str, branch: str):
    print("finding sha", repo, path, branch)
    res = httpx.get(f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}", headers={"Authorization": f"Bearer {token}"})
    print("status", res.status_code)
    if res.status_code == 404:
        print("new file")
        return None
    if res.status_code != 200:
        print("github error", res.text)
        raise HTTPException(status_code=400, detail="GitHub request failed, connect GitHub again")
    sha = res.json()["sha"]
    print("sha", sha)
    return sha


def send_github(token: str, method: str, path: str, body: dict):
    print("github send", method, path)
    res = httpx.request(method, "https://api.github.com" + path, json=body, headers={"Authorization": f"Bearer {token}"})
    print("status", res.status_code)
    if res.status_code not in (200, 201):
        print("github error", res.text)
        raise HTTPException(status_code=400, detail=f"GitHub request failed: {res.json().get('message')}")
    return res.json()
