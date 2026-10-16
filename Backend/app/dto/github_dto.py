from pydantic import BaseModel

class GithubCodeDto(BaseModel):
    code: str
