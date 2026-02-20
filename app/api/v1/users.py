from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.logging import get_logger
from app.security.dependencies import get_current_user, get_db
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user
from app.core.rate_limiter import limiter
from fastapi import Request

router = APIRouter(prefix="/users", tags=["users"])

logger = get_logger("users")

@router.get("/me")
@limiter.limit("60/minute")  # 60 requests per minute
def get_me(
    request: Request,  # required for slowapi
    user: User = Depends(get_current_user),
):
    return {"id": user.id, "email": user.email, "role": user.role}

@router.post("", response_model=UserResponse)
@limiter.limit("10/minute")
def create_user_endpoint(
    request: Request,  # required for slowapi
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_user(
        db=db,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )
    except Exception:
        raise HTTPException(status_code=400, detail="Bad Request Data")