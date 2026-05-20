from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.core.security import generate_verification_token
from backend.schemas.auth import ResendVerificationRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Посилання вже використане або недійсне",
        )

    if user.token_expires_at and user.token_expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Посилання прострочене. Запросіть нове",
        )

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
