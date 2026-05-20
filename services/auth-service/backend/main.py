import traceback
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.database import Base
from backend.database.session import engine, SessionLocal
from backend.models.user import User
from backend.middleware import SecurityHeadersMiddleware, RateLimitMiddleware, AuditLogMiddleware
from backend.routers import (
    auth_register,
    auth_login,
    auth_verify,
    users as users_router,
    admin_users as admin_users_router,
)

app = FastAPI(title="Auth Service", version="2.0.0")


def init_db():
    Base.metadata.create_all(bind=engine)
    print("[OK] Auth service: Database tables created")


def init_default_users():
    from backend.core.enums import UserRole
    from backend.core.security import hash_password

    db: Session = SessionLocal()
    try:
        default_users = [
            {"username": "admin", "password": "Admin1pass", "role": UserRole.SYSTEM_ADMIN, "name": "Адміністратор"},
            {"username": "manager", "password": "Manager1", "role": UserRole.MANAGER, "name": "Менеджер"},
            {"username": "client", "password": "Client1", "role": UserRole.CLIENT, "name": "Клієнт"},
        ]
        for ud in default_users:
            if not db.query(User).filter(User.username == ud["username"]).first():
                user = User(
                    username=ud["username"],
                    password=hash_password(ud["password"]),
                    role=ud["role"].value,
                    name=ud.get("name"),
                    is_verified=True,
                )
                db.add(user)
                db.commit()
                print(f"[OK] User created: {ud['username']} ({ud['role'].value})")
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
app.add_middleware(AuditLogMiddleware)


@app.on_event("startup")
async def startup_event():
    init_db()
    init_default_users()
    print("[OK] Auth service: Startup complete")


app.include_router(admin_users_router.router)
app.include_router(auth_register.router)
app.include_router(auth_login.router)
app.include_router(auth_verify.router)
app.include_router(users_router.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service", "version": "2.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"ERROR: {request.method} {request.url} -> {type(exc).__name__}: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
