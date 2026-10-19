from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .review import Finding


class FixResult(BaseModel):
    fixed_code: str = Field(description="the complete file after the fix")
    explanation: str = Field(description="1-2 sentences about what was changed")
    test_code: str = Field(description="the complete pytest file that checks the fix, or empty if no test was asked for")


class FixDto(BaseModel):
    repo: str
    pr_number: int
    finding: Finding


class FixResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    repo: str
    pr_number: int
    file: str
    title: str
    explanation: str
    old_code: str
    new_code: str
    test_file: str
    test_code: str
    status: str
    pr_url: str | None
    ci_status: str | None
    attempts: int
    created_at: datetime
