from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.security.dependencies import get_db
from app.services.user_service import authenticate_user
from app.security.jwt import create_access_token
from app.config.env_config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------
# Request schema
# ---------------------------
class LoginRequest(BaseModel):
    email: str
    password: str


# ---------------------------
# Login endpoint
# ---------------------------
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {"access_token": token, "token_type": "bearer"}
