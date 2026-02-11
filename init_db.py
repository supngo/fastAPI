# init_db.py
from app.config.db_config import Base, engine, SessionLocal
from app.services.user_service import create_user
from app.security.roles import Role

# ---------------------------
# 1. Create all tables
# ---------------------------
Base.metadata.create_all(bind=engine)
print("✅ Database tables created")

# ---------------------------
# 2. Seed initial users
# ---------------------------
db = SessionLocal()
try:
    # Admin user
    if not db.query(Base.metadata.tables['users']).filter_by(email="admin@example.com").first():
        create_user(db, email="admin@example.com", password="admin", role=Role.ADMIN)
        print("✅ Admin user created: admin@example.com / admin")

    # Regular user
    if not db.query(Base.metadata.tables['users']).filter_by(email="user@example.com").first():
        create_user(db, email="user@example.com", password="password", role=Role.USER)
        print("✅ Regular user created: user@example.com / password")
finally:
    db.close()

print("🎉 Database setup complete")
