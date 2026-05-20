from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from backend.database import Base
from backend.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    name = Column(String(255), nullable=True)
    password = Column(String, nullable=False)
    role = Column(String, default=UserRole.CLIENT.value, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), unique=True, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
