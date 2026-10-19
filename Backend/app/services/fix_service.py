import base64
import time

from fastapi import HTTPException
from langchain_core.prompts import PromptTemplate

from ..core.llm import model
from ..models.user import User
from ..schemas.fix import FixResult
from ..schemas.review import Finding
from .github_service import call_github, send_github

prompt = PromptTemplate(
    template="""You are a senior software engineer. Fix only this one problem in the file below.

Problem: {title}
Line: {line}
Why it is a problem: {explanation}
How to fix it: {suggestion}

Change only what is needed for this problem and keep everything else exactly the same.
Return the complete fixed file.

File: {file}
{code}""",
    input_variables=["title", "line", "explanation", "suggestion", "file", "code"],
)

structured_model = model.with_structured_output(FixResult)
chain = prompt | structured_model



def make_fix(user: User, repo: str, pr_number: int, finding: Finding):
    token = get_token(user)
    pr = get_pr(token, repo, pr_number)
    code, _ = read_file(token, repo, finding.file, pr["head"]["ref"])

    try:
        result = chain.invoke({
            "title": finding.title,
            "line": finding.line,
            "explanation": finding.explanation,
            "suggestion": finding.suggestion,
            "file": finding.file,
            "code": code,
        })
        
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI fix failed: {e}")
    
    return {"file": finding.file, "old_code": code, "new_code": result.fixed_code, "explanation": result.explanation}




def apply_fix(user: User, repo: str, pr_number: int, file: str, new_code: str, title: str):
    token = get_token(user)
    pr = get_pr(token, repo, pr_number)
    pr_branch = pr["head"]["ref"]
    _, sha = read_file(token, repo, file, pr_branch)

    new_branch = f"gitaudit/fix-pr{pr_number}-{int(time.time())}"
    send_github(token, "POST", f"/repos/{repo}/git/refs", {
        "ref": f"refs/heads/{new_branch}",
        "sha": pr["head"]["sha"],
    })
    send_github(token, "PUT", f"/repos/{repo}/contents/{file}", {
        "message": f"Fix: {title}",
        "content": base64.b64encode(new_code.encode()).decode(),
        "sha": sha,
        "branch": new_branch,
    })
    new_pr = send_github(token, "POST", f"/repos/{repo}/pulls", {
        "title": f"Fix: {title}",
        "head": new_branch,
        "base": pr_branch,
        "body": f"AI fix for **{title}** in `{file}`, found while reviewing #{pr_number}.\n\nReview it before merging.",
    })
    return {"pr_url": new_pr["html_url"]}



def get_token(user: User):
    if user.github_token is None:
        raise HTTPException(status_code=400, detail="Connect GitHub first")
    return user.github_token



def get_pr(token: str, repo: str, pr_number: int):
    pr = call_github(token, f"/repos/{repo}/pulls/{pr_number}")
    if pr["head"]["repo"] is None or pr["head"]["repo"]["full_name"] != repo:
        raise HTTPException(status_code=400, detail="Fixes work only for pull requests from a branch of this repo, not from a fork")
    return pr



def read_file(token: str, repo: str, path: str, branch: str):
    data = call_github(token, f"/repos/{repo}/contents/{path}?ref={branch}")
    code = base64.b64decode(data["content"]).decode()
    return code, data["sha"]
