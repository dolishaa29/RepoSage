from pydantic import BaseModel

class RepoResponse(BaseModel):
    id: int
    full_name: str
    private: bool
    language: str | None
    description: str | None
    html_url: str
    updated_at: str

class PullResponse(BaseModel):
    number: int
    title: str
    author: str
    html_url: str
