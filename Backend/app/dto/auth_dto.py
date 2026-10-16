from pydantic import BaseModel, EmailStr

class RegisterDto(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginDto(BaseModel):
    email: EmailStr
    password: str
