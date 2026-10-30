from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Finding(BaseModel):
    file: str = Field(description="file path from the diff")
    line: int | None = Field(description="line number in the new code, or null if unsure")
    severity: Literal["high", "medium", "low"]
    category: Literal["bug", "security", "bad_practice"]
    title: str = Field(description="short name of the problem")
    explanation: str = Field(description="why this is a problem")
    suggestion: str = Field(description="how to fix it")

class AgentResult(BaseModel):
    findings: list[Finding]


class ReviewResult(BaseModel):
    summary: str = Field(description="2-3 sentences about the pull request and its overall risk")
    risk: Literal["high", "medium", "low"] = Field(description="how risky it is to merge this pull request")
    what_changed: str = Field(description="1-3 short sentences about what this pull request changes")
    what_to_test: str = Field(description="1-3 short sentences about what a person should test")
    findings: list[Finding]


class ReviewDto(BaseModel):
    repo: str        
    pr_number: int


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    repo: str
    pr_number: int
    pr_title: str
    ai: str | None
    summary: str
    risk: str | None
    pr_summary: str | None
    findings: list[Finding]
    created_at: datetime
