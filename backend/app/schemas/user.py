# Pydantic request/response schemas for user accounts.
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# Body of POST /auth/register.
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


# Public-facing user shape — deliberately excludes hashed_password.
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime

    class Config:
        from_attributes = True
