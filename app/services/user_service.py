from typing import Generator
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.user import User
from app.security.roles import Role
from app.core.exceptions import UnauthorizedError

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------
# Helper: password verification
# ---------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------
# Helper: hash a new password
# ---------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ---------------------------
# Get user by email
# ---------------------------
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


# ---------------------------
# Authenticate user
# ---------------------------
def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user with email and password.
    Raises UnauthorizedError if invalid.
    Returns User object if valid.
    """
    user = get_user_by_email(db, email)
    if not user:
        raise UnauthorizedError("Invalid credentials")

    if not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid credentials")

    return user


# ---------------------------
# Create a new user (optional)
# ---------------------------
def create_user(db: Session, email: str, password: str, role: str = Role.USER) -> User:
    hashed_password = hash_password(password)
    new_user = User(email=email, hashed_password=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
