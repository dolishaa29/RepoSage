from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    github_username: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
