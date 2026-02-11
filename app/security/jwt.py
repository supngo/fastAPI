from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config.env_config import JWT_SECRET, JWT_ALGORITHM
from app.core.exceptions import UnauthorizedError

def create_access_token(data: dict, expires_minutes: int):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise UnauthorizedError("Invalid or expired token")
