from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User


class EmailAlreadyRegistered(Exception):
    pass


class UsernameAlreadyTaken(Exception):
    pass


def register_user(db: Session, email: str, username: str, password: str) -> User:
    if db.query(User).filter(User.email == email).first():
        raise EmailAlreadyRegistered
    if db.query(User).filter(User.username == username).first():
        raise UsernameAlreadyTaken

    user = User(email=email, username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
