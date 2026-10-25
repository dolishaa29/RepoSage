import difflib
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .review import Finding


class FixResult(BaseModel):
    explanation: str = Field(description="1-2 sentences about what was changed")
    test_file: str = Field(description="repo-relative path of the unit test file you created, or empty")
    test_command: str = Field(description="shell command, run from the repo root on ubuntu-latest, that installs what is needed and runs only this test, or empty")


class Change(BaseModel):
    file: str
    old_code: str
    new_code: str

    @computed_field
    def diff(self) -> str:
        lines = difflib.unified_diff(self.old_code.splitlines(), self.new_code.splitlines(), self.file, self.file, lineterm="")
        return "\n".join(lines)


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
    changes: list[Change]
    test_file: str
    test_command: str
    status: str
    pr_url: str | None
    ci_status: str | None
    attempts: int
    created_at: datetime
