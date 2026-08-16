# Password hashing and JWT helpers — the "ID card printer and ID checker"
# for the app (see CLAUDE.md Session 4). Used by auth_service.py and deps.py.
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Turns a plaintext password into an irreversible hash for storage.
def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


# Checks a login attempt's password against the stored hash.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


# Issues a signed JWT for `subject` (the user id) that expires after
# jwt_access_token_expire_minutes.
def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# Verifies a JWT's signature/expiry and returns the subject (user id), or
# None if the token is missing, expired, or tampered with.
def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
    return payload.get("sub")
