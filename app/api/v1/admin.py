from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.security.dependencies import require_roles, get_db
from app.security.roles import Role
from app.models.user import User
from app.core.rate_limiter import limiter
from fastapi import Request

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
@limiter.limit("60/minute")  # 60 requests per minute
def get_admin_stats(
    request: Request,
    user: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    total_users = db.query(User).count()
    return {"admin_id": user.id, "total_users": total_users}
