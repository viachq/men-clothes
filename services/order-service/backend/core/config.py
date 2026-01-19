"""
Order Service configuration settings.
"""
import os
from pathlib import Path

# Database URL - окрема база для order-service
# Підтримка Docker (через environment variable) та локальної розробки
if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    # Локальна розробка
    project_root = Path(__file__).resolve().parents[4]
    db_path = project_root / "order.db"
    DATABASE_URL = f"sqlite:///{db_path.as_posix()}"
    
    # Створити директорію для БД якщо не існує (для Docker)
    db_dir = db_path.parent
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)

# JWT Settings - однаковий ключ для всіх мікросервісів
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ippt-project-dev-secret-key-fixed-for-local-development-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = 10080  # 7 days

# Single Store Mode
DEFAULT_STORE_ID = 1

# Service Configuration
SERVICE_NAME = "order-service"
SERVICE_PORT = 8003

# Inter-service communication URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8002")

# LiqPay Settings
LIQPAY_PUBLIC_KEY = os.getenv("LIQPAY_PUBLIC_KEY", "sandbox_i92249544327")
LIQPAY_PRIVATE_KEY = os.getenv("LIQPAY_PRIVATE_KEY", "sandbox_nPi9dv3hV5WstAz8NKCtJgaUWweoX0NGBGmCVVBE")
LIQPAY_SANDBOX_MODE = os.getenv("LIQPAY_SANDBOX_MODE", "true").lower() == "true"
