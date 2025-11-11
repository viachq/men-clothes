"""
Application configuration settings.
"""
import os
from pathlib import Path

# Database URL
project_root = Path(__file__).resolve().parents[2]
db_path = project_root / "app.db"
DATABASE_URL = f"sqlite:///{db_path.as_posix()}"

# JWT Settings
# Fixed secret key for development (use environment variable in production)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ippt-project-dev-secret-key-fixed-for-local-development-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = 10080  # 7 days (7 * 24 * 60) - convenient for development

# Single Restaurant Mode
DEFAULT_RESTAURANT_ID = 1  # This app is designed for single restaurant

# Telegram Bot Settings (hardcoded for educational project)
TELEGRAM_BOT_TOKEN = "8322734845:AAGQDbGSboYa9qP5G6H-omfAnnPL0GDiwQE"
TELEGRAM_ADMIN_CHAT_IDS = [827612750]
TELEGRAM_NOTIFICATIONS_ENABLED = True
