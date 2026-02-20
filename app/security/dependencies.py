from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Generator

from app.security.token import TokenPayload, decode_access_token
from app.config.db_config import SessionLocal
from app.models.user import User
from app.security.roles import Role
import uuid
import logging
logger = logging.getLogger("app.auth")

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
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract current user from JWT token and fetch from DB.
    """
    try:
        payload_dict = decode_access_token(credentials.credentials)
        
        # Validate payload structure + email format
        payload = TokenPayload(**payload_dict)
        user_id = uuid.UUID(payload.sub)  # 🔥 convert string -> UUID
    except Exception:
        logger.exception(f"Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.exception(f"User {payload.email} not found")
        raise HTTPException(status_code=401, detail="User not found")
    
    logger.info(
        "user_authenticated",
        extra={
            "event": "user_authenticated",
            "request_id": getattr(request.state, "request_id", None),
            "user_id": str(user.id),
            "email": user.email,
        },
    )

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
            logger.exception(f"User {user.email} is not permitted for this service")
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return role_checker
