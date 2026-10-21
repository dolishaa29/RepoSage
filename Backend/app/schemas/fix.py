from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .review import Finding


class FixResult(BaseModel):
    fixed_code: str = Field(description="the complete file after the fix")
    explanation: str = Field(description="1-2 sentences about what was changed")
    test_file: str = Field(description="repo-relative path of the unit test file, or empty if this file cannot have a unit test")
    test_code: str = Field(description="the complete unit test file that checks the fix, or empty")
    test_command: str = Field(description="shell command, run from the repo root on ubuntu-latest, that installs what is needed and runs only this test, or empty")


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
    test_command: str
    status: str
    pr_url: str | None
    ci_status: str | None
    attempts: int
    created_at: datetime
