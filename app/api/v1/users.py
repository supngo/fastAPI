from fastapi import APIRouter, Depends
from app.security.dependencies import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def get_me(
    user: User = Depends(get_current_user),
):
    return {"id": user.id, "email": user.email, "role": user.role}
