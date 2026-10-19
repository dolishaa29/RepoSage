from pydantic import BaseModel, Field

from .review import Finding


class FixResult(BaseModel):
    fixed_code: str = Field(description="the complete file after the fix")
    explanation: str = Field(description="1-2 sentences about what was changed")


class FixDto(BaseModel):
    repo: str
    pr_number: int
    finding: Finding


class FixResponse(BaseModel):
    file: str
    old_code: str
    new_code: str
    explanation: str


class ApplyFixDto(BaseModel):
    repo: str
    pr_number: int
    file: str
    new_code: str
    title: str


class ApplyFixResponse(BaseModel):
    pr_url: str
