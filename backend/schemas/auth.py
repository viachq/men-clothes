from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)
    email: str | None = None
    phone: str | None = None
    name: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль повинен містити хоча б одну цифру")
        if not any(c.isalpha() for c in v):
            raise ValueError("Пароль повинен містити хоча б одну літеру")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str | None = None
    phone: str | None = None
    name: str | None = None
    role: str
    is_active: bool = True
    is_verified: bool = False

    model_config = {"from_attributes": True}


class ResendVerificationRequest(BaseModel):
    username: str


class UserProfileUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    old_password: str | None = None
    password: str | None = Field(None, min_length=6, max_length=72)
