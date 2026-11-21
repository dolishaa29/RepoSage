from pydantic import BaseModel, ConfigDict


class GithubAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    github_accounts: list[GithubAccountResponse] = []

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
