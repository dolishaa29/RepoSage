from typing import Any
from pydantic import BaseModel


class JobResponse(BaseModel):
    job_id: int
    status: str
    result: Any = None
    error: str | None = None
