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

class ReviewResult(BaseModel):
    summary: str = Field(description="2-3 sentences about the pull request and its overall risk")
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
    findings: list[Finding]
    created_at: datetime
