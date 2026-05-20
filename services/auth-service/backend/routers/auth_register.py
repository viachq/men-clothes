from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.core.enums import UserRole
from backend.core.security import hash_password, generate_verification_token
from backend.schemas.auth import RegisterRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Це ім'я користувача вже зайняте")

    if payload.email:
        email_exists = db.query(User).filter(User.email == payload.email).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="Цей email вже зареєстровано")

    verification_token, token_expires_at = generate_verification_token()

    new_user = User(
        username=payload.username,
        password=hash_password(payload.password),
        email=payload.email,
        phone=payload.phone,
        name=payload.name,
        role=UserRole.CLIENT.value,
        is_verified=False,
        verification_token=verification_token,
        token_expires_at=token_expires_at,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Реєстрація успішна. Лист для підтвердження надіслано на вашу пошту",
        "verification_token": verification_token,
        "user": UserOut.model_validate(new_user).model_dump(),
    }
