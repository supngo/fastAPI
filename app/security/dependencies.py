from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Generator

from app.security.token import decode_access_token
from app.config.db_config import SessionLocal
from app.models.user import User
from app.security.roles import Role

# ---------------------------
# Security scheme
# ---------------------------
security = HTTPBearer()  # expects "Authorization: Bearer <token>" header


# ---------------------------
# DB session dependency
# ---------------------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# Get current user from JWT token
# ---------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract current user from JWT token and fetch from DB.
    """
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ---------------------------
# Role-based access control
# ---------------------------
def require_roles(*roles: Role):
    """
    FastAPI dependency to enforce user roles.
    Usage: Depends(require_roles(Role.ADMIN))
    """
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return role_checker
