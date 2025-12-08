from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.users.models import User
from app.modules.users.schemas import User as UserSchema

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def read_current_user(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get current user.
    """
    return current_user
