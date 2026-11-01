from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import User
from app.security import DUMMY_HASH, hash_password, verify_password


class EmailAlreadyRegistered(Exception):
    pass


def create_user(db: Session, *, email: str, name: str, password: str, timezone: str) -> User:
    user = User(
        email=email.strip().lower(),
        name=name.strip(),
        timezone=timezone,
        password_hash=hash_password(password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyRegistered()
    db.refresh(user)
    return user


def authenticate(db: Session, *, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None:
        verify_password(password, DUMMY_HASH)  # burn the same time as a real check
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user