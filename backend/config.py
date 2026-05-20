import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{(PROJECT_ROOT / 'shop.db').as_posix()}",
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "ippt-project-dev-secret-key-fixed-for-local-development-2024",
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = 10080  # 7 days

SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

LIQPAY_PUBLIC_KEY = os.getenv("LIQPAY_PUBLIC_KEY", "sandbox_i92249544327")
LIQPAY_PRIVATE_KEY = os.getenv(
    "LIQPAY_PRIVATE_KEY",
    "sandbox_nPi9dv3hV5WstAz8NKCtJgaUWweoX0NGBGmCVVBE",
)
LIQPAY_SANDBOX_MODE = os.getenv("LIQPAY_SANDBOX_MODE", "true").lower() == "true"
