from sqlalchemy import Column, Integer, String
from app.config.db_config import Base
from app.security.roles import Role

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=Role.USER)
