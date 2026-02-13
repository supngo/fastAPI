from app.config.db_config import Base, engine

# Import all models so they are registered with Base.metadata
from app.models.user import User  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401


def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


if __name__ == "__main__":
    init_db()
