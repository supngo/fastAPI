from fastapi import APIRouter, Header, Body, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.security.dependencies import get_db, get_current_user
from app.services.user_service import authenticate_user
from app.services.refresh_token_service import (
    get_valid_refresh_token,
    revoke_token,
    create_refresh_token,
)
from app.security.token import create_access_token, generate_refresh_token
from app.core.logging import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])

logger = get_logger("auth")

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
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    
    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
    })

    raw_refresh = generate_refresh_token()
    create_refresh_token(db, user.id, raw_refresh)

    # Set HTTP-only cookie for browser clients
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh,
        httponly=True,
        secure=False,  # True in production (HTTPS)
        samesite="lax",
        path="/auth/refresh",
    )

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh, # for API clients
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # Allow header usage for API clients
    x_refresh_token: str | None = Header(default=None, alias="X-Refresh-Token"),
    # Allow body usage as fallback
    body_token: str | None = Body(default=None, embed=True),
):
    """
    Supports:
    1. Cookie: refresh_token
    2. Header: X-Refresh-Token: <token>
    3. Body: { "refresh_token": "..." }
    """

    raw_token = (
        request.cookies.get("refresh_token")
        or x_refresh_token
        or body_token
    )
    logger.info("-> x_refresh_token:", x_refresh_token)
    logger.info("-> body_token:", body_token)
    logger.info("-> cookies:", request.cookies.get("refresh_token"))

    if not raw_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    token = get_valid_refresh_token(db, raw_token)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # 🔁 Rotate refresh token
    new_raw = generate_refresh_token()
    new_token = create_refresh_token(db, token.user_id, new_raw)

    revoke_token(db, token, replaced_by_id=new_token.id)

    # Create new access token
    access_token = create_access_token({"sub": str(token.user_id)})

    # Set cookie for browser clients
    response.set_cookie(
        key="refresh_token",
        value=new_raw,
        httponly=True,
        secure=False,  # True in production (HTTPS)
        samesite="lax",
        path="/auth/refresh",
    )

    return {
        "access_token": access_token,
        "refresh_token": new_raw,  # for API-only clients
        "token_type": "bearer",
    }

@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Body(default=None),
):
    raw_token = request.cookies.get("refresh_token") or refresh_token

    if raw_token:
        token = get_valid_refresh_token(db, raw_token)
        if token:
            revoke_token(db, token)

    response.delete_cookie("refresh_token", path="/auth/refresh")
    return {"message": "Logged out"}

@router.post("/logout-all")
def logout_all (
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(RefreshToken).filter(
    RefreshToken.user_id == current_user.id,
    RefreshToken.revoked == False
    ).update( 
        {"revoked": True},
        synchronize_session=False,
    )
    db.commit()