import base64

from fastapi import HTTPException

from ..github_service import call_github, find_file_sha, get_github_text, send_github


def get_pr(token: str, repo: str, pr_number: int):
    print("getting pr", repo, pr_number)
    pr = call_github(token, f"/repos/{repo}/pulls/{pr_number}")
    print("pr branch", pr["head"]["ref"], pr["head"]["sha"])
    if pr["head"]["repo"] is None or pr["head"]["repo"]["full_name"] != repo:
        print("fork pr")
        raise HTTPException(status_code=400, detail="Fixes work only for pull requests from a branch of this repo, not from a fork")
    return pr


def read_file(token: str, repo: str, path: str, branch: str):
    print("reading file", path, branch)
    data = call_github(token, f"/repos/{repo}/contents/{path}?ref={branch}")
    code = base64.b64decode(data["content"]).decode()
    print("file code", code)
    return code


def save_file(token: str, repo: str, path: str, code: str, branch: str, message: str):
    print("saving file", path, branch, message)
    body = {"message": message, "content": base64.b64encode(code.encode()).decode(), "branch": branch}
    sha = find_file_sha(token, repo, path, branch)
    if sha:
        body["sha"] = sha
    send_github(token, "PUT", f"/repos/{repo}/contents/{path}", body)
    print("file saved", path)


def create_branch(token: str, repo: str, branch: str, sha: str):
    print("creating branch", branch, sha)
    send_github(token, "POST", f"/repos/{repo}/git/refs", {"ref": f"refs/heads/{branch}", "sha": sha})
    print("branch created")


def open_pr(token: str, repo: str, title: str, head: str, base: str, body: str):
    print("opening pr", title, head, base)
    pr = send_github(token, "POST", f"/repos/{repo}/pulls", {"title": title, "head": head, "base": base, "body": body})
    print("pr opened", pr["html_url"])
    return pr


def latest_run(token: str, repo: str, branch: str):
    print("latest run", branch)
    head_sha = call_github(token, f"/repos/{repo}/branches/{branch}")["commit"]["sha"]
    print("head sha", head_sha)
    runs = call_github(token, f"/repos/{repo}/actions/runs?branch={branch}&head_sha={head_sha}")["workflow_runs"]
    print("runs count", len(runs))
    if runs:
        print("run", runs[0]["id"], runs[0]["status"], runs[0]["conclusion"])
    return runs[0] if runs else None


def test_log(token: str, repo: str, run_id: int):
    print("getting log", run_id)
    jobs = call_github(token, f"/repos/{repo}/actions/runs/{run_id}/jobs")["jobs"]
    log = get_github_text(token, f"/repos/{repo}/actions/jobs/{jobs[0]['id']}/logs")[-4000:]
    print("log", log)
    return log
