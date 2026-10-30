from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterDto(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)

class LoginDto(BaseModel):
    email: EmailStr
    password: str


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
