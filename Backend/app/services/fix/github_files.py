import base64

from fastapi import HTTPException

from ..github_service import call_github, find_file_sha, get_github_text, send_github


def get_pr(token: str, repo: str, pr_number: int):
    pr = call_github(token, f"/repos/{repo}/pulls/{pr_number}")
    if pr["head"]["repo"] is None or pr["head"]["repo"]["full_name"] != repo:
        raise HTTPException(status_code=400, detail="Fixes work only for pull requests from a branch of this repo, not from a fork")
    return pr


def read_file(token: str, repo: str, path: str, branch: str):
    data = call_github(token, f"/repos/{repo}/contents/{path}?ref={branch}")
    return base64.b64decode(data["content"]).decode()


def save_file(token: str, repo: str, path: str, code: str, branch: str, message: str):
    body = {"message": message, "content": base64.b64encode(code.encode()).decode(), "branch": branch}
    sha = find_file_sha(token, repo, path, branch)
    if sha:
        body["sha"] = sha
    send_github(token, "PUT", f"/repos/{repo}/contents/{path}", body)


def create_branch(token: str, repo: str, branch: str, sha: str):
    send_github(token, "POST", f"/repos/{repo}/git/refs", {"ref": f"refs/heads/{branch}", "sha": sha})


def open_pr(token: str, repo: str, title: str, head: str, base: str, body: str):
    return send_github(token, "POST", f"/repos/{repo}/pulls", {"title": title, "head": head, "base": base, "body": body})


def latest_run(token: str, repo: str, branch: str):
    head_sha = call_github(token, f"/repos/{repo}/branches/{branch}")["commit"]["sha"]
    runs = call_github(token, f"/repos/{repo}/actions/runs?branch={branch}&head_sha={head_sha}")["workflow_runs"]
    return runs[0] if runs else None


def test_log(token: str, repo: str, run_id: int):
    jobs = call_github(token, f"/repos/{repo}/actions/runs/{run_id}/jobs")["jobs"]
    return get_github_text(token, f"/repos/{repo}/actions/jobs/{jobs[0]['id']}/logs")[-4000:]
