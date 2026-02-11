import os

APP_NAME = os.getenv("APP_NAME", "my-backend")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
