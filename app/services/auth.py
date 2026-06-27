from sqlalchemy.orm import Session

from app.auth import verify_password
from app.models.users import User
from app.schemas.auth import UserOut


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        username=user.username,
        fullname=user.fullname,
        level=user.level or "",
        is_admin=(user.level == "Administrator"),
    )


def get_user(db: Session, username: str) -> UserOut | None:
    if not username or not username.strip():
        return None
    user = db.get(User, username)
    return _to_user_out(user) if user else None


def authenticate_user(db: Session, username: str, password: str) -> UserOut | None:
    if not username or not username.strip() or not password:
        return None
    user = db.get(User, username)
    if user is None:
        return None
    if not user.password:
        return None
    try:
        if not verify_password(password, user.password):
            return None
    except Exception:
        return None
    return _to_user_out(user)
