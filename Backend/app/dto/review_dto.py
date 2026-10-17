from pydantic import BaseModel

class ReviewDto(BaseModel):
    repo: str        # "owner/name"
    pr_number: int
