from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/balance", response_model=dict)
async def get_balance(current_user: User = Depends(get_current_user)):
    """Получить текущий баланс"""
    return {"balance": float(current_user.balance)}

