from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(_oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Require a valid JWT and return the logged-in user, or raise 401."""
    user = _resolve_user(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user_optional(
    token: str | None = Depends(_oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """Return the logged-in user if a valid JWT was sent, otherwise None (anonymous)."""
    return _resolve_user(token, db)


def _resolve_user(token: str | None, db: Session) -> User | None:
    if not token:
        return None
    user_id = decode_access_token(token)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == int(user_id)).first()
