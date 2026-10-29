from datetime import datetime
from pydantic import BaseModel


class RepoCount(BaseModel):
    repo: str
    findings: int

class DayCount(BaseModel):
    day: str
    reviews: int
    fixes: int

class Activity(BaseModel):
    kind: str          # "review" or "fix"
    repo: str
    pr_number: int
    title: str
    status: str
    created_at: datetime


class StatsResponse(BaseModel):
    reviews: int
    findings: int
    fixes: int
    prs_opened: int
    ci_passed: int
    ci_failed: int
    severity: dict[str, int]
    category: dict[str, int]
    fix_status: dict[str, int]
    top_repos: list[RepoCount]
    last_14_days: list[DayCount]
    recent: list[Activity]
