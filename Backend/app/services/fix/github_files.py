import base64

from fastapi import HTTPException

from ..github_service import call_github, find_file_sha, get_github_text, send_github


# a PR from a fork lives in someone else's repo, and we cannot create branches there
def get_pr(token: str, repo: str, pr_number: int):
    pr = call_github(token, f"/repos/{repo}/pulls/{pr_number}")
    if pr["head"]["repo"] is None or pr["head"]["repo"]["full_name"] != repo:
        raise HTTPException(status_code=400, detail="Fixes work only for pull requests from a branch of this repo, not from a fork")
    return pr


# GitHub sends file content as base64
def read_file(token: str, repo: str, path: str, branch: str):
    data = call_github(token, f"/repos/{repo}/contents/{path}?ref={branch}")
    return base64.b64decode(data["content"]).decode()


# one PUT = one commit. An existing file needs its current sha, so nobody's newer change is overwritten.
def save_file(token: str, repo: str, path: str, code: str, branch: str, message: str):
    body = {"message": message, "content": base64.b64encode(code.encode()).decode(), "branch": branch}
    sha = find_file_sha(token, repo, path, branch)
    if sha:
        body["sha"] = sha
    send_github(token, "PUT", f"/repos/{repo}/contents/{path}", body)


# a branch is just a name pointing at a commit
def create_branch(token: str, repo: str, branch: str, sha: str):
    send_github(token, "POST", f"/repos/{repo}/git/refs", {"ref": f"refs/heads/{branch}", "sha": sha})


def open_pr(token: str, repo: str, title: str, head: str, base: str, body: str):
    return send_github(token, "POST", f"/repos/{repo}/pulls", {"title": title, "head": head, "base": base, "body": body})


# the CI run for the branch's latest commit (older runs tested older code), or None if it has not started
def latest_run(token: str, repo: str, branch: str):
    head_sha = call_github(token, f"/repos/{repo}/branches/{branch}")["commit"]["sha"]
    runs = call_github(token, f"/repos/{repo}/actions/runs?branch={branch}&head_sha={head_sha}")["workflow_runs"]
    return runs[0] if runs else None


# the end of the test log, where the error is. Kept short so the AI prompt stays small.
def test_log(token: str, repo: str, run_id: int):
    jobs = call_github(token, f"/repos/{repo}/actions/runs/{run_id}/jobs")["jobs"]
    return get_github_text(token, f"/repos/{repo}/actions/jobs/{jobs[0]['id']}/logs")[-4000:]
