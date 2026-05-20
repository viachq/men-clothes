from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.enums import UserRole
from backend.security import (
    hash_password, verify_password, create_access_token, generate_verification_token,
)
from backend.schemas.auth import (
    RegisterRequest, LoginRequest, UserOut, ResendVerificationRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Це ім'я користувача вже зайняте")

    if payload.email:
        if db.query(User).filter(User.email == payload.email).first():
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


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Посилання вже використане або недійсне")

    if user.token_expires_at and user.token_expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Посилання прострочене. Запросіть нове")

    user.is_verified = True
    user.verification_token = None
    user.token_expires_at = None
    db.commit()
    return {"message": "Email успішно підтверджено"}


@router.post("/resend-verification")
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or user.is_verified:
        return {"message": "Якщо акаунт існує і не підтверджений, лист буде надіслано"}

    verification_token, expires_at = generate_verification_token()
    user.verification_token = verification_token
    user.token_expires_at = expires_at
    db.commit()

    return {
        "message": "Якщо акаунт існує і не підтверджений, лист буде надіслано",
        "verification_token": verification_token,
    }
