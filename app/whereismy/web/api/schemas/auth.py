# app/whereismy/web/api/schemas/auth.py
from pydantic import BaseModel

class LoginData(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None
