from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.deps import get_current_user, require_roles
from backend.security import hash_password, verify_password
from backend.schemas.auth import UserOut, UserProfileUpdate
from backend.enums import UserRole

router = APIRouter(tags=["users"])


# ── Profile ──────────────────────────────────────────────────────────

@router.get("/users/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user).model_dump()


@router.put("/users/me")
def update_my_profile(
    body: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.name is not None:
        current_user.name = body.name
    if body.email is not None:
        exists = db.query(User).filter(User.email == body.email, User.id != current_user.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Цей email вже зареєстровано")
        current_user.email = body.email
    if body.phone is not None:
        current_user.phone = body.phone
    if body.password:
        if not body.old_password or not verify_password(body.old_password, current_user.password):
            raise HTTPException(status_code=400, detail="Невірний поточний пароль")
        current_user.password = hash_password(body.password)

    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user).model_dump()


@router.get("/users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user).model_dump()


@router.get("/users/username/{username}")
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user).model_dump()


# ── Admin ────────────────────────────────────────────────────────────

@router.get("/admin/users/")
def get_all_users(
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users]


@router.put("/admin/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        new_role = UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}",
        )

    user.role = new_role.value
    db.commit()
    db.refresh(user)
    return {"message": "Role updated successfully", "user_id": user.id, "username": user.username, "role": user.role}
