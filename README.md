# Men's Clothes - Інтернет-магазин чоловічого одягу

Повнофункціональний вебзастосунок для інтернет-магазину чоловічого одягу з адмін-панеллю, аналітикою, системою відгуків та інтеграцією з LiqPay.

## Швидкий старт (Docker)

Найпростіший спосіб запустити проект:

```bash
git clone https://github.com/viachq/men-clothes.git
cd men-clothes
docker-compose up --build
```

Після запуску:
- **Магазин (клієнт):** http://localhost:5174
- **Адмін-панель:** http://localhost:5173
- **API документація:** http://localhost:8000/docs

### Тестові користувачі

| Логін | Пароль | Роль |
|-------|--------|------|
| `admin` | `Admin1pass` | Системний адміністратор |
| `manager` | `Manager1` | Менеджер |
| `client` | `Client1` | Клієнт |

## Локальний запуск (без Docker)

### Вимоги

- Python 3.11+ (рекомендовано 3.12+)
- Node.js 18+ (рекомендовано 20+)
- Git

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Admin Frontend

```powershell
cd admin
npm install
npm run dev
```

### Client Frontend

```powershell
cd client
npm install
npm run dev
```

## Архітектура

```
                    +-----------------+
                    |   Client App    |  :5174
                    |  React + Vite   |
                    +--------+--------+
                             |
                    +--------v--------+
                    |   Backend API   |  :8000
                    |    FastAPI      |
                    |   (unified)     |
                    +--------+--------+
                             |
                    +--------v--------+
                    |    SQLite       |
                    |   (shop.db)    |
                    +-----------------+
                             |
                    +--------+--------+
                    |   Admin Panel   |  :5173
                    |  React + Vite   |
                    +-----------------+
```

### Backend (Python/FastAPI)

Єдиний API сервер на порту 8000:
- JWT аутентифікація (HS256, 7-денні токени)
- Ролі: `SYSTEM_ADMIN`, `MANAGER`, `CLIENT`
- SQLAlchemy ORM + SQLite (shop.db)
- Ціни зберігаються в копійках (integer)

**API модулі:**
- `/auth/*` - реєстрація, логін, верифікація email
- `/products/*`, `/categories/*` - каталог товарів
- `/variants/*` - розміри (S/M/L/XL) з per-size stock
- `/cart/*` - кошик
- `/orders/*` - оформлення замовлень
- `/payments/*` - LiqPay інтеграція (sandbox)
- `/reviews/*` - відгуки (тільки після покупки)
- `/promo/*` - промокоди
- `/admin/analytics/*` - аналітика (summary, detailed, advanced)

### Frontend (React 19 + TypeScript + Vite + Tailwind CSS)

**Клієнтська частина:**
- Каталог з фільтрами, пошуком, сортуванням
- Картки товарів з бейджами (Sale/New) та старою ціною
- Модалка товару з розмірами, відгуками, рейтингом
- Кошик з формою оформлення (ПІБ, телефон, метод доставки)
- Промокоди, LiqPay оплата
- Темна/світла тема

**Адмін-панель:**
- Дашборд з графіками замовлень
- CRUD товарів (бейджі, стара ціна, варіанти розмірів)
- Управління замовленнями зі статусами
- Промокоди
- Модерація відгуків
- Аналітика (revenue, top products, customer segmentation, retention, cross-sell)
- Темна/світла тема

## Технології

| Шар | Технології |
|-----|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy, SQLite, python-jose (JWT), bcrypt |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Axios, Recharts, Lucide Icons |
| DevOps | Docker, Docker Compose, Nginx |
| Оплата | LiqPay (sandbox) |

## Структура проекту

```
men-clothes/
├── backend/                 # Unified FastAPI backend
│   ├── main.py             # App entry + seed data
│   ├── config.py           # Settings (DB, JWT, LiqPay)
│   ├── database.py         # SQLAlchemy engine
│   ├── models/             # ORM models
│   ├── routers/            # API endpoints
│   ├── schemas/            # Pydantic schemas
│   ├── middleware.py       # Security headers, rate limit, audit
│   ├── requirements.txt
│   └── Dockerfile
├── admin/                   # Admin React app
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── client/                  # Client React app
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## Docker

```powershell
# Зібрати та запустити
docker-compose up --build

# В фоновому режимі
docker-compose up -d --build

# Логи
docker-compose logs -f

# Зупинити
docker-compose down

# Зупинити + очистити БД
docker-compose down -v
```

Контейнери:
- `mens-clothes-backend` - FastAPI на порту 8000
- `mens-clothes-client` - Nginx + React на порту 5174
- `mens-clothes-admin` - Nginx + React на порту 5173

## Змінні середовища

| Змінна | За замовчуванням | Опис |
|--------|-----------------|------|
| `DATABASE_URL` | `sqlite:///shop.db` | URL бази даних |
| `JWT_SECRET_KEY` | dev key | Секрет для JWT токенів |
| `LIQPAY_PUBLIC_KEY` | sandbox key | LiqPay публічний ключ |
| `LIQPAY_PRIVATE_KEY` | sandbox key | LiqPay приватний ключ |
