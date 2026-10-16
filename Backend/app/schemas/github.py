from pydantic import BaseModel

class UrlResponse(BaseModel):
    url: str

class RepoResponse(BaseModel):
    id: int
    full_name: str
    private: bool
    language: str | None
    description: str | None
    html_url: str
    updated_at: str
