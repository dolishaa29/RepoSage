from pydantic import BaseModel

class ReviewDto(BaseModel):
    repo: str       
    pr_number: int
