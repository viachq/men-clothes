from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.core.security import verify_password, create_access_token
from backend.schemas.auth import LoginRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Невірне ім'я користувача або пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Акаунт деактивовано")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Підтвердіть email для входу")

    token = create_access_token(user.username)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user).model_dump(),
    }
