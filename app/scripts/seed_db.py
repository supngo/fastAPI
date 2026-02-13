from sqlalchemy.orm import Session

from app.config.db_config import SessionLocal

# IMPORTANT: import both models so SQLAlchemy registers relationships
from app.models.user import User
# from app.models.refresh_token import RefreshToken  # <-- add this

from app.services.user_service import hash_password

def seed_users():
    db: Session = SessionLocal()

    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                hashed_password=hash_password("Admin123!"),
                role="admin",
            )
            db.add(admin)
            print("Created admin user: admin@example.com / Admin123!")

        # Check if normal user exists
        user = db.query(User).filter(User.email == "user@example.com").first()
        if not user:
            user = User(
                email="user@example.com",
                hashed_password=hash_password("User123!"),
                role="user",
            )
            db.add(user)
            print("Created normal user: user@example.com / User123!")

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
