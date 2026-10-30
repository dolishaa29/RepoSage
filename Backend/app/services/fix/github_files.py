from fastapi import HTTPException
from ..github_service import call_github, get_github_text, github_request, send_github


def get_pr(token: str, repo: str, pr_number: int):
    pr = call_github(token, f"/repos/{repo}/pulls/{pr_number}")
    if pr["head"]["repo"] is None or pr["head"]["repo"]["full_name"] != repo:
        raise HTTPException(status_code=400, detail="Fixes work only for pull requests from a branch of this repo, not from a fork")
    return pr


def branch_sha(token: str, repo: str, branch: str):
    sha = call_github(token, f"/repos/{repo}/branches/{branch}")["commit"]["sha"]
    return sha



def commit_files(token: str, repo: str, branch: str, files: dict, message: str):
    head = branch_sha(token, repo, branch)
    commit = call_github(token, f"/repos/{repo}/git/commits/{head}")
    tree_items = call_github(token, f"/repos/{repo}/git/trees/{commit['tree']['sha']}?recursive=1")["tree"]
    modes = {item["path"]: item["mode"] for item in tree_items}
    entries = [{"path": path, "mode": modes.get(path, "100644"), "type": "blob", "content": code} for path, code in files.items()]
    tree = send_github(token, "POST", f"/repos/{repo}/git/trees", {"base_tree": commit["tree"]["sha"], "tree": entries})
    new_commit = send_github(token, "POST", f"/repos/{repo}/git/commits", {"message": message, "tree": tree["sha"], "parents": [head]})
    send_github(token, "PATCH", f"/repos/{repo}/git/refs/heads/{branch}", {"sha": new_commit["sha"]})



def create_branch(token: str, repo: str, branch: str, sha: str):
    send_github(token, "POST", f"/repos/{repo}/git/refs", {"ref": f"refs/heads/{branch}", "sha": sha})


def delete_branch(token: str, repo: str, branch: str):
    try:
        github_request("DELETE", f"https://api.github.com/repos/{repo}/git/refs/heads/{branch}", headers={"Authorization": f"Bearer {token}"})
    except HTTPException:
        pass




def open_pr(token: str, repo: str, title: str, head: str, base: str, body: str):
    pr = send_github(token, "POST", f"/repos/{repo}/pulls", {"title": title, "head": head, "base": base, "body": body})
    return pr



def latest_run(token: str, repo: str, branch: str):
    head_sha = branch_sha(token, repo, branch)
    runs = call_github(token, f"/repos/{repo}/actions/runs?branch={branch}&head_sha={head_sha}")["workflow_runs"]
    return runs[0] if runs else None



def test_log(token: str, repo: str, run_id: int):
    jobs = call_github(token, f"/repos/{repo}/actions/runs/{run_id}/jobs")["jobs"]
    if len(jobs) == 0:
        return "The test run had no jobs, so there is no log. Check the workflow and the test command."
    log = get_github_text(token, f"/repos/{repo}/actions/jobs/{jobs[0]['id']}/logs")[-4000:]
    return log
