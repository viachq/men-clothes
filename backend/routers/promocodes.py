from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import require_roles
from backend.enums import UserRole
from backend.models.promo_code import PromoCode
from backend.schemas.promo import (
    PromoCodeCreate, PromoCodeUpdate, PromoCodeOut,
    PromoValidateRequest, PromoValidateResponse,
)

router = APIRouter(prefix="/promo", tags=["promo"])


def _validate_promo(db: Session, code: str, order_total: int) -> tuple[bool, int, str]:
    promo = db.query(PromoCode).filter(PromoCode.code == code.upper()).first()
    if not promo:
        return False, 0, "Промокод не знайдено"
    if not promo.is_active:
        return False, 0, "Промокод неактивний"
    now = datetime.utcnow()
    if promo.valid_from and now < promo.valid_from:
        return False, 0, "Промокод ще не діє"
    if promo.valid_until and now > promo.valid_until:
        return False, 0, "Термін дії промокоду закінчився"
    if promo.max_uses is not None and promo.current_uses >= promo.max_uses:
        return False, 0, "Промокод вичерпано"
    if promo.min_order_amount and order_total < promo.min_order_amount:
        return False, 0, f"Мінімальна сума замовлення: {promo.min_order_amount} коп."

    if promo.discount_percent:
        discount = int(order_total * promo.discount_percent / 100)
        message = f"Знижка {promo.discount_percent}% застосована"
    elif promo.discount_amount:
        discount = min(promo.discount_amount, order_total)
        message = f"Фіксована знижка {promo.discount_amount} коп. застосована"
    else:
        return False, 0, "Промокод налаштовано некоректно"
    return True, discount, message


@router.post("/validate", response_model=PromoValidateResponse)
def validate_promo_code(body: PromoValidateRequest, db: Session = Depends(get_db)):
    valid, discount, message = _validate_promo(db, body.code, body.order_total)
    return PromoValidateResponse(valid=valid, discount=discount, message=message)


@router.get("/", response_model=list[PromoCodeOut])
def list_promo_codes(
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    return db.query(PromoCode).order_by(PromoCode.created_at.desc()).all()


@router.post("/", response_model=PromoCodeOut, status_code=201)
def create_promo_code(
    body: PromoCodeCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    if body.discount_percent and body.discount_amount:
        raise HTTPException(status_code=400, detail="Вкажіть або відсоток знижки, або фіксовану суму, але не обидва")
    if not body.discount_percent and not body.discount_amount:
        raise HTTPException(status_code=400, detail="Вкажіть відсоток знижки або фіксовану суму")

    code_upper = body.code.upper()
    if db.query(PromoCode).filter(PromoCode.code == code_upper).first():
        raise HTTPException(status_code=409, detail="Промокод з таким кодом вже існує")

    promo_data = body.model_dump()
    promo_data["code"] = code_upper
    promo = PromoCode(**promo_data)
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo


@router.put("/{promo_id}", response_model=PromoCodeOut)
def update_promo_code(
    promo_id: int,
    body: PromoCodeUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    promo = db.query(PromoCode).filter(PromoCode.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Промокод не знайдено")

    data = body.model_dump(exclude_unset=True)
    if "code" in data:
        data["code"] = data["code"].upper()

    new_percent = data.get("discount_percent", promo.discount_percent)
    new_amount = data.get("discount_amount", promo.discount_amount)
    if new_percent and new_amount:
        raise HTTPException(status_code=400, detail="Вкажіть або відсоток знижки, або фіксовану суму, але не обидва")

    for field, value in data.items():
        setattr(promo, field, value)
    db.commit()
    db.refresh(promo)
    return promo


@router.delete("/{promo_id}", status_code=204)
def deactivate_promo_code(
    promo_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    promo = db.query(PromoCode).filter(PromoCode.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Промокод не знайдено")
    promo.is_active = False
    db.commit()
