# IPPT Microservices - Мікросервісний вебзастосунок з CI/CD та Kubernetes

Проект для практики: мікросервісний вебзастосунок для системи замовлення одягу з автоматизованим CI/CD pipeline та деплоєм у Kubernetes.

## 📋 Зміст

- [Архітектура](#архітектура)
- [Технології](#технології)
- [Структура проекту](#структура-проекту)
- [Локальний запуск](#локальний-запуск)
- [Docker](#docker)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD](#cicd)
- [Тестування](#тестування)
- [API Документація](#api-документація)

## 🏗️ Архітектура

Проект реалізований як мікросервісна архітектура з трьома основними backend сервісами та двома frontend додатками:

### Backend Services

1. **Auth Service** (порт 8001)
   - Аутентифікація та авторизація користувачів
   - JWT токени
   - Управління користувачами та ролями
   - Endpoints: `/auth/register`, `/auth/login`, `/users/*`

2. **Catalog Service** (порт 8002)
   - Управління категоріями товарів
   - Управління товарами (menu items)
   - CRUD операції для каталогу
   - Endpoints: `/categories/*`, `/products/*`

3. **Order Service** (порт 8003)
   - Управління кошиком (cart)
   - Створення та управління замовленнями
   - Платежі
   - Статистика замовлень
   - Endpoints: `/cart/*`, `/orders/*`, `/payments/*`

### Frontend Applications

1. **Client Frontend** (порт 5174)
   - Клієнтський інтерфейс для перегляду товарів та замовлення
   - React + TypeScript + Vite

2. **Admin Frontend** (порт 5173)
   - Адмін панель для управління системою
   - Управління товарами, замовленнями, статистика
   - React + TypeScript + Vite

### Бази даних

Кожен сервіс має свою SQLite базу даних:
- `auth.db` - користувачі та ролі
- `catalog.db` - категорії та товари
- `order.db` - замовлення, кошики, платежі

## 🛠️ Технології

### Backend
- **Python 3.13** - мова програмування
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для роботи з БД
- **SQLite** - база даних (для production рекомендується PostgreSQL)
- **JWT** - аутентифікація (python-jose)

### Frontend
- **React 19** - UI фреймворк
- **TypeScript** - типізація
- **Vite** - збірка та dev server
- **Tailwind CSS** - стилізація
- **Axios** - HTTP клієнт

### DevOps
- **Docker** - контейнеризація
- **Docker Compose** - локальний запуск
- **Kubernetes** - оркестрація контейнерів
- **GitHub Actions** - CI/CD pipeline

## 📁 Структура проекту

```
ippt-microservices/
├── services/
│   ├── auth-service/          # Auth мікросервіс
│   │   ├── backend/
│   │   │   ├── tests/         # Unit tests (95% coverage)
│   │   │   ├── routers/       # API endpoints
│   │   │   ├── models/        # Database models
│   │   │   ├── core/          # Security, config
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── catalog-service/       # Catalog мікросервіс
│   └── order-service/         # Order мікросервіс
├── admin/                     # Admin frontend
├── client/                    # Client frontend
├── k8s/                      # Kubernetes manifests
│   ├── auth-service/
│   ├── catalog-service/
│   ├── order-service/
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── ingress.yaml
├── .github/
│   └── workflows/
│       └── auth-service-tests.yml  # CI/CD pipeline
├── docker-compose.yml         # Docker Compose конфігурація
├── DOCKER.md                  # Docker документація
└── README.md                  # Цей файл
```

## 🚀 Локальний запуск

### Вимоги

- Python 3.11+
- Node.js 18+
- npm або yarn

### Запуск без Docker

1. **Клонувати репозиторій:**
```bash
git clone https://github.com/viachq/ippt-microservices.git
cd ippt-microservices
```

2. **Запустити backend сервіси:**

```bash
# Auth Service
cd services/auth-service
python -m pip install -r requirements.txt
set PYTHONPATH=%CD%
python -m uvicorn backend.main:app --reload --port 8001

# Catalog Service (в новому терміналі)
cd services/catalog-service
python -m pip install -r requirements.txt
set PYTHONPATH=%CD%
python -m uvicorn backend.main:app --reload --port 8002

# Order Service (в новому терміналі)
cd services/order-service
python -m pip install -r requirements.txt
set PYTHONPATH=%CD%
python -m uvicorn backend.main:app --reload --port 8003
```

3. **Запустити frontend:**

```bash
# Admin Frontend
cd admin
npm install
npm run dev

# Client Frontend (в новому терміналі)
cd client
npm install
npm run dev
```

Або використати скрипт `START.bat` для Windows.

### Доступ до сервісів

- Auth Service: http://localhost:8001
- Catalog Service: http://localhost:8002
- Order Service: http://localhost:8003
- Admin Frontend: http://localhost:5173
- Client Frontend: http://localhost:5174

## 🐳 Docker

### Запуск з Docker Compose

```bash
# Зібрати та запустити всі сервіси
docker-compose up --build

# Запуск в фоновому режимі
docker-compose up -d --build

# Перегляд логів
docker-compose logs -f

# Зупинка
docker-compose down
```

Детальна інструкція: [DOCKER.md](DOCKER.md)

### Dockerfile для кожного сервісу

Кожен сервіс має свій Dockerfile:
- `services/auth-service/Dockerfile`
- `services/catalog-service/Dockerfile`
- `services/order-service/Dockerfile`
- `admin/Dockerfile`
- `client/Dockerfile`

## ☸️ Kubernetes Deployment

### Вимоги

- Kubernetes кластер (minikube, k3s, kind, або cloud)
- kubectl встановлений та налаштований

### Швидкий старт

1. **Підготовка Docker images:**

```bash
# Для minikube
eval $(minikube docker-env)

# Зібрати images
docker build -t auth-service:latest ./services/auth-service
docker build -t catalog-service:latest ./services/catalog-service
docker build -t order-service:latest ./services/order-service
docker build -t client-frontend:latest ./client
docker build -t admin-frontend:latest ./admin
```

2. **Деплой в Kubernetes:**

```bash
# Створити namespace
kubectl apply -f k8s/namespace.yaml

# Застосувати конфігурацію
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Застосувати сервіси
kubectl apply -f k8s/auth-service/
kubectl apply -f k8s/catalog-service/
kubectl apply -f k8s/order-service/
kubectl apply -f k8s/client-frontend/
kubectl apply -f k8s/admin-frontend/

# Застосувати Ingress (опціонально)
kubectl apply -f k8s/ingress.yaml
```

3. **Перевірка статусу:**

```bash
kubectl get pods -n food-delivery
kubectl get svc -n food-delivery
```

Детальна інструкція: [k8s/README.md](k8s/README.md)

### Kubernetes Компоненти

- **Deployment** - 2 replicas для кожного сервісу
- **Service** - ClusterIP для внутрішньої комунікації
- **ConfigMap** - конфігурація сервісів
- **Secret** - JWT ключі та токени
- **Ingress** - маршрутизація трафіку
- **Health Checks** - liveness та readiness probes

## 🔄 CI/CD

### GitHub Actions Pipeline

CI/CD pipeline налаштований в `.github/workflows/auth-service-tests.yml`:

**Етапи pipeline:**
1. **Lint** - перевірка коду з flake8
2. **Tests** - запуск unit tests з pytest
3. **Coverage** - перевірка покриття коду (>= 70%)
4. **Reports** - завантаження coverage reports

### Запуск тестів локально

```bash
cd services/auth-service
pytest backend/tests/ -v --cov=backend --cov-report=term-missing --cov-fail-under=70
```

## 🧪 Тестування

### Unit Tests

Проект містить комплексні unit tests для `auth-service`:

- **Coverage: 95%** (вище мінімального 70%)
- **76 тестів** - всі проходять
- Тести для security functions, API endpoints, dependencies, models

### Структура тестів

```
services/auth-service/backend/tests/
├── conftest.py              # Pytest fixtures
├── test_security.py         # Security functions tests
├── test_auth_register.py   # Registration tests
├── test_auth_login.py       # Login tests
├── test_users.py            # User endpoints tests
├── test_deps.py             # Dependencies tests
└── test_models.py           # Models tests
```

### Запуск тестів

```bash
cd services/auth-service
pytest backend/tests/ -v
```

## 📚 API Документація

Кожен сервіс має автоматичну OpenAPI/Swagger документацію:

- **Auth Service**: http://localhost:8001/docs
- **Catalog Service**: http://localhost:8002/docs
- **Order Service**: http://localhost:8003/docs

## 🔐 Default Users

Після першого запуску створюються тестові користувачі:

- **admin** / **admin** - System Admin
- **manager** / **manager** - Manager
- **client** / **client** - Client

## 📝 Ліцензія

Цей проект створено для навчальних цілей.

## 👥 Автори

Проект виконано в рамках практики з мікросервісних архітектур та DevOps.

---

**GitHub Repository**: https://github.com/viachq/ippt-microservices
