# Архітектура системи (діаграма розгортання / компонентів)

Мікросервісна архітектура: 3 незалежні backend-сервіси (FastAPI), 2 SPA-фронтенди
(React), кожен сервіс має власну базу даних SQLite. Міжсервісна взаємодія —
через HTTP (REST), автентифікація — спільний JWT (HS256).

```mermaid
flowchart TB
    subgraph Client["Клієнтська частина"]
        CF["Client SPA<br/>React + Vite<br/>:5174"]
        AF["Admin SPA<br/>React + Vite<br/>:5173"]
    end

    subgraph Backend["Серверна частина (мікросервіси, FastAPI)"]
        AUTH["auth-service<br/>:8001<br/>реєстрація, вхід,<br/>JWT, ролі, верифікація email"]
        CAT["catalog-service<br/>:8002<br/>товари, категорії,<br/>розміри, відгуки"]
        ORD["order-service<br/>:8003<br/>кошик, замовлення,<br/>оплата, промокоди, аналітика"]
    end

    subgraph DB["Бази даних (SQLite, по одній на сервіс)"]
        AUTHDB[("auth.db")]
        CATDB[("catalog.db")]
        ORDDB[("order.db")]
    end

    EXT["LiqPay<br/>(зовнішній платіжний шлюз)"]

    CF -->|REST /auth, /users| AUTH
    CF -->|REST /products, /categories, /reviews, /variants| CAT
    CF -->|REST /cart, /orders, /promo, /payments| ORD
    AF -->|REST /admin/*| AUTH
    AF -->|REST /admin/*| CAT
    AF -->|REST /admin/*| ORD

    AUTH --> AUTHDB
    CAT --> CATDB
    ORD --> ORDDB

    CAT -.->|перевірка JWT / даних користувача| AUTH
    ORD -.->|перевірка JWT / даних користувача| AUTH
    ORD -.->|назви товарів для аналітики| CAT
    ORD -->|форма оплати + callback| EXT

    classDef svc fill:#1f2937,stroke:#111,color:#fff
    classDef db fill:#374151,stroke:#111,color:#fff
    class AUTH,CAT,ORD svc
    class AUTHDB,CATDB,ORDDB db
```

## Технологічний стек

| Шар | Технології |
|-----|-----------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn |
| БД | SQLite (по одній на мікросервіс) |
| Автентифікація | JWT (HS256, python-jose), bcrypt |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Axios, Recharts |
| Оплата | LiqPay (sandbox) |
| Розгортання | Docker, docker-compose, Kubernetes, GitHub Actions CI/CD |
| Тестування | pytest, pytest-cov (193 тести, покриття 69–94%) |
