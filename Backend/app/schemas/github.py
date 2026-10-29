from pydantic import BaseModel


class GithubCodeDto(BaseModel):
    code: str


class RepoResponse(BaseModel):
    id: int
    full_name: str
    private: bool
    language: str | None
    description: str | None
    html_url: str
    updated_at: str
    account: str

class PullResponse(BaseModel):
    number: int
    title: str
    author: str
    html_url: str


class IndexResponse(BaseModel):
    chunks: int
