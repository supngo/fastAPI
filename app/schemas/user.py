from uuid import UUID
from pydantic import BaseModel, EmailStr


# Request body for POST /users
class UserCreate(BaseModel):
    email: EmailStr  # <-- automatic email validation
    password: str
    role: str


# Response model
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str

    class Config:
        from_attributes = True  # allows SQLAlchemy -> Pydantic conversion


# Token payload validation (as you requested)
class TokenPayload(BaseModel):
    sub: UUID  # user id
    exp: int   # expiration timestamp
