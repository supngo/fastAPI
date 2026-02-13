from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import os
from app.models.refresh_token import RefreshToken
from app.security.token import hash_token
from dotenv import load_dotenv
from app.core.logging import get_logger


load_dotenv()

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

logger = get_logger("refresh_token")

def create_refresh_token(db: Session, user_id, raw_token: str) -> RefreshToken:
    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_valid_refresh_token(db: Session, raw_token: str) -> RefreshToken | None:
    token_hash = hash_token(raw_token)
    token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
        )
        .first()
    )
    if not token:
        return None

    # 🚨 Reuse detection: token already revoked but being used again
    if token.revoked:
        handle_token_reuse(db, token)
        return None
    
    # Expiry check (safe for naive/aware datetimes)
    expires_at = token.expires_at

    # Normalize to timezone-aware UTC if DB returned naive datetime
    if expires_at is None:
        return None

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    # Compare safely using UTC-aware datetime
    if expires_at < datetime.now(timezone.utc):
        return None

    return token

def handle_token_reuse(db: Session, token: RefreshToken):
    """
    If a revoked token is reused, assume compromise:
    revoke all refresh tokens for that user.
    """
    logger.warning(f"Refresh token reuse detected for user_id={token.user_id}")
    db.query(RefreshToken).filter(
        RefreshToken.user_id == token.user_id,
        RefreshToken.revoked == False,
    ).update({"revoked": True})

    db.commit()

def revoke_token(db: Session, token: RefreshToken, replaced_by_id=None):
    token.revoked = True
    token.replaced_by_token_id = replaced_by_id
    db.commit()
