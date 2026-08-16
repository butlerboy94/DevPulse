# Pydantic schemas for JWT-related request/response bodies.
from pydantic import BaseModel


# Response shape of POST /auth/login.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Decoded contents of a JWT's payload (see core/security.py).
class TokenPayload(BaseModel):
    sub: str | None = None
