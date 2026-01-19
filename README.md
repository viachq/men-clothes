# IPPT Microservices - Мікросервісний вебзастосунок з CI/CD та Kubernetes

Проект для практики: мікросервісний вебзастосунок для системи замовлення одягу з автоматизованим CI/CD pipeline та деплоєм у Kubernetes.

## Зміст

- [Швидкий старт](#швидкий-старт)
- [Налаштування для нових користувачів](#налаштування-для-нових-користувачів)
- [Архітектура](#архітектура)
- [Технології](#технології)
- [Структура проекту](#структура-проекту)
- [Локальний запуск](#локальний-запуск)
- [Docker](#docker)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD](#cicd)
- [Тестування](#тестування)
- [API Документація](#api-документація)

## Швидкий старт

### Мінімальні вимоги

- **Python 3.11+** (рекомендовано 3.13)
- **Node.js 18+** (рекомендовано 20+)
- **Docker Desktop** (для Docker запуску)
- **Git** для клонування репозиторію

### Швидкий запуск з Docker (рекомендовано)

```bash
# 1. Клонувати репозиторій
git clone https://github.com/YOUR_GITHUB_USERNAME/ippt-microservices.git
cd ippt-microservices

# 2. Запустити всі сервіси одним команд
docker-compose up --build

# 3. Відкрити в браузері:
# - Admin Panel: http://localhost:5173
# - Client App: http://localhost:5174
# - Auth API: http://localhost:8001/docs
# - Catalog API: http://localhost:8002/docs
# - Order API: http://localhost:8003/docs
```

**Default користувачі:**
- `admin` / `admin` - System Admin
- `manager` / `manager` - Manager  
- `client` / `client` - Client

## Налаштування для нових користувачів

### Як склонувати та налаштувати проект для себе

Якщо ви хочете використовувати цей проект як основу для свого власного проекту:

#### Крок 1: Клонувати репозиторій

```bash
# Створити форк або клонувати
git clone https://github.com/YOUR_GITHUB_USERNAME/ippt-microservices.git
cd ippt-microservices
```

#### Крок 2: Налаштувати свій GitHub репозиторій

1. **Створити новий репозиторій на GitHub:**
   - Перейдіть на https://github.com/new
   - Назва: `ippt-microservices` (або ваша назва)
   - Вибрати Public або Private
   - НЕ ініціалізувати з README (ми вже маємо)

2. **Змінити remote URL:**
```bash
# Видалити поточний remote
git remote remove origin

# Додати ваш GitHub репозиторій
git remote add origin https://github.com/ВАШ_GITHUB_USERNAME/ippt-microservices.git

# Перевірити
git remote -v
```

3. **Змінити назву в проекті (опціонально):**
```bash
# Замінити всі згадки старого назви на ваше
# Наприклад, якщо змінюєте "YOUR_GITHUB_USERNAME" на "yourusername":
# Windows PowerShell
(Get-Content .github/workflows/ci-cd.yml) -replace 'YOUR_GITHUB_USERNAME', 'yourusername' | Set-Content .github/workflows/ci-cd.yml
(Get-Content k8s/*/deployment.yaml) -replace 'YOUR_GITHUB_USERNAME', 'yourusername' | Set-Content k8s/*/deployment.yaml

# Linux/Mac
sed -i 's/YOUR_GITHUB_USERNAME/yourusername/g' .github/workflows/ci-cd.yml
sed -i 's/YOUR_GITHUB_USERNAME/yourusername/g' k8s/*/deployment.yaml
```

4. **Закомітити та запушити:**
```bash
git add .
git commit -m "Initial commit - forked from original project"
git push -u origin main
```

#### Крок 3: Встановити необхідне програмне забезпечення

##### Windows

1. **Python 3.11+**
   - Завантажити з https://www.python.org/downloads/
   - Під час встановлення обов'язково вибрати "Add Python to PATH"

2. **Node.js 18+**
   - Завантажити LTS версію з https://nodejs.org/
   - Встановити, npm встановиться автоматично

3. **Docker Desktop**
   - Завантажити з https://www.docker.com/products/docker-desktop
   - Встановити та запустити Docker Desktop

4. **Git**
   - Завантажити з https://git-scm.com/download/win
   - Або використати GitHub Desktop

##### Linux (Ubuntu/Debian)

```bash
# Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Docker
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
# Потрібно вийти та зайти знову

# Git
sudo apt install git
```

##### macOS

```bash
# Встановити Homebrew якщо немає
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python
brew install python@3.13

# Node.js
brew install node@20

# Docker Desktop
brew install --cask docker

# Git (зазвичай вже встановлений)
```

#### Крок 4: Перевірити встановлення

```bash
# Перевірити версії
python --version    # Має бути 3.11+
node --version      # Має бути 18+
npm --version       # Має бути встановлено
docker --version    # Має бути встановлено
git --version       # Має бути встановлено

# Перевірити Docker
docker ps
```

#### Крок 5: Налаштувати CI/CD для свого GitHub (опціонально)

1. **Оновити GitHub Container Registry URL в CI/CD:**

Відредагувати `.github/workflows/ci-cd.yml`:
```yaml
# Знайти і замінити:
env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ghcr.io/ВАШ_GITHUB_USERNAME/ippt-microservices
```

Відредагувати всі `k8s/*/deployment.yaml` файли:
```yaml
# Знайти і замінити в усіх файлах:
image: ghcr.io/ВАШ_GITHUB_USERNAME/ippt-microservices-auth-service:${{ github.sha }}
image: ghcr.io/ВАШ_GITHUB_USERNAME/ippt-microservices-catalog-service:${{ github.sha }}
# ... і так далі
```

2. **Налаштувати GitHub Secrets (для автоматичного деплою):**

Якщо хочете автоматичний деплой в Kubernetes:

- Перейдіть: **Settings** → **Secrets and variables** → **Actions**
- Додати `KUBECONFIG` secret (base64 закодований kubeconfig файл)
- Детальна інструкція: [docs/KUBERNETES_SETUP.md](docs/KUBERNETES_SETUP.md)

**Важливо:** Без `KUBECONFIG` secret, pipeline все одно працюватиме, але пропустить крок деплою.

## Архітектура

Проект реалізований як мікросервісна архітектура з трьома основними backend сервісами та двома frontend додатками:

### Backend Services

1. **Auth Service** (порт 8001)
   - Аутентифікація та авторизація користувачів
   - JWT токени (JSON Web Tokens)
   - Управління користувачами та ролями
   - Ролі: `SYSTEM_ADMIN`, `MANAGER`, `CLIENT`
   - Endpoints: `/auth/register`, `/auth/login`, `/users/*`
   - Database: `auth.db` (SQLite)

2. **Catalog Service** (порт 8002)
   - Управління категоріями товарів
   - Управління товарами (menu items)
   - CRUD операції для каталогу
   - Кешування категорій та продуктів
   - Endpoints: `/categories/*`, `/products/*`, `/admin/categories/*`, `/admin/products/*`
   - Database: `catalog.db` (SQLite)
   - Залежить від: Auth Service (для авторизації)

3. **Order Service** (порт 8003)
   - Управління кошиком (cart)
   - Створення та управління замовленнями
   - Платежі (інтеграція з LiqPay)
   - Статистика замовлень
   - Endpoints: `/cart/*`, `/orders/*`, `/payments/*`, `/admin/orders/*`, `/admin/stats/*`
   - Database: `order.db` (SQLite)
   - Залежить від: Auth Service, Catalog Service

### Frontend Applications

1. **Client Frontend** (порт 5174)
   - Клієнтський інтерфейс для перегляду товарів та замовлення
   - React 19 + TypeScript + Vite
   - Tailwind CSS для стилізації
   - Функціонал: перегляд каталогу, кошик, оформлення замовлень

2. **Admin Frontend** (порт 5173)
   - Адмін панель для управління системою
   - Управління товарами, замовленнями, статистика
   - React 19 + TypeScript + Vite
   - Tailwind CSS для стилізації
   - Доступ: тільки для користувачів з ролями `SYSTEM_ADMIN` або `MANAGER`

### Комунікація між сервісами

```
┌─────────────┐
│   Client    │────────┐
│  Frontend   │        │
└─────────────┘        │
                       │ HTTP/REST API
┌─────────────┐        │
│   Admin     │────────┤
│  Frontend   │        │
└─────────────┘        │
                       ↓
        ┌──────────────────────────┐
        │    Auth Service          │
        │  (JWT Token Validation)  │
        └──────────────────────────┘
                  ↑         ↑
                  │         │
        ┌─────────┘         └─────────┐
        │                              │
┌───────┴────────┐          ┌─────────┴──────┐
│ Catalog        │          │ Order          │
│ Service        │◄─────────┤ Service        │
│                │  HTTP    │                │
└────────────────┘          └────────────────┘
```

### Бази даних

Кожен сервіс має свою SQLite базу даних (для production рекомендується PostgreSQL):

- `auth.db` - користувачі та ролі
- `catalog.db` - категорії та товари
- `order.db` - замовлення, кошики, платежі

## Технології

### Backend
- **Python 3.13** - мова програмування
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для роботи з БД
- **SQLite** - база даних (для production рекомендується PostgreSQL)
- **JWT** - аутентифікація (python-jose)
- **Pytest** - тестування (покриття >= 70%)

### Frontend
- **React 19** - UI фреймворк
- **TypeScript** - типізація
- **Vite** - збірка та dev server
- **Tailwind CSS** - стилізація
- **Axios** - HTTP клієнт
- **ESLint** - лінтинг коду

### DevOps
- **Docker** - контейнеризація
- **Docker Compose** - локальний запуск
- **Kubernetes** - оркестрація контейнерів
- **GitHub Actions** - CI/CD pipeline
- **GitHub Container Registry** - зберігання Docker образів

## Структура проекту

```
ippt-microservices/
├── services/                    # Backend мікросервіси
│   ├── auth-service/           # Auth мікросервіс
│   │   ├── backend/
│   │   │   ├── tests/          # Unit tests (95% coverage)
│   │   │   ├── routers/        # API endpoints
│   │   │   ├── models/         # Database models
│   │   │   ├── core/           # Security, config
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── pytest.ini
│   ├── catalog-service/        # Catalog мікросервіс
│   └── order-service/          # Order мікросервіс
├── admin/                      # Admin frontend
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── client/                     # Client frontend
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── k8s/                        # Kubernetes manifests
│   ├── auth-service/
│   ├── catalog-service/
│   ├── order-service/
│   ├── client-frontend/
│   ├── admin-frontend/
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── ingress.yaml
│   └── namespace.yaml
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # CI/CD pipeline
├── docker-compose.yml          # Docker Compose конфігурація
├── DOCKER.md                   # Docker документація
├── docs/
│   └── KUBERNETES_SETUP.md     # Kubernetes setup інструкції
└── README.md                   # Цей файл
```

## Локальний запуск

### Варіант 1: Docker Compose (рекомендовано)

Найпростіший спосіб запустити всі сервіси:

```bash
# 1. Клонувати репозиторій (якщо ще не зробили)
git clone https://github.com/YOUR_GITHUB_USERNAME/ippt-microservices.git
cd ippt-microservices

# 2. Запустити всі сервіси
docker-compose up --build

# Запуск в фоновому режимі
docker-compose up -d --build

# Перегляд логів
docker-compose logs -f

# Перегляд логів конкретного сервісу
docker-compose logs -f auth-service

# Зупинка
docker-compose down

# Зупинка з видаленням volumes (очищення БД)
docker-compose down -v
```

### Варіант 2: Локальний запуск без Docker

Для розробки або якщо немає Docker:

#### Windows

1. **Встановити залежності для backend:**

```powershell
# Для кожного сервісу окремо
cd services/auth-service
python -m pip install -r requirements.txt
python -m pip install pytest pytest-cov  # для тестів

cd ..\catalog-service
python -m pip install -r requirements.txt
python -m pip install pytest pytest-cov

cd ..\order-service
python -m pip install -r requirements.txt
python -m pip install pytest pytest-cov
```

2. **Запустити backend сервіси (в окремих терміналах):**

```powershell
# Термінал 1 - Auth Service
cd services/auth-service
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn backend.main:app --reload --port 8001

# Термінал 2 - Catalog Service
cd services/catalog-service
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn backend.main:app --reload --port 8002

# Термінал 3 - Order Service
cd services/order-service
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn backend.main:app --reload --port 8003
```

3. **Встановити залежності для frontend:**

```powershell
# Admin Frontend
cd admin
npm install

# Client Frontend
cd ..\client
npm install
```

4. **Запустити frontend (в окремих терміналах):**

```powershell
# Термінал 4 - Admin Frontend
cd admin
npm run dev

# Термінал 5 - Client Frontend
cd client
npm run dev
```

Або використати готовий скрипт `START.bat`:
```powershell
.\START.bat
```

#### Linux/macOS

1. **Встановити залежності для backend:**

```bash
# Для кожного сервісу
cd services/auth-service
python3 -m pip install -r requirements.txt
python3 -m pip install pytest pytest-cov

cd ../catalog-service
python3 -m pip install -r requirements.txt
python3 -m pip install pytest pytest-cov

cd ../order-service
python3 -m pip install -r requirements.txt
python3 -m pip install pytest pytest-cov
```

2. **Запустити backend сервіси (в окремих терміналах):**

```bash
# Термінал 1 - Auth Service
cd services/auth-service
export PYTHONPATH=$(pwd)
python3 -m uvicorn backend.main:app --reload --port 8001

# Термінал 2 - Catalog Service
cd services/catalog-service
export PYTHONPATH=$(pwd)
python3 -m uvicorn backend.main:app --reload --port 8002

# Термінал 3 - Order Service
cd services/order-service
export PYTHONPATH=$(pwd)
python3 -m uvicorn backend.main:app --reload --port 8003
```

3. **Встановити та запустити frontend:**

```bash
# Admin Frontend
cd admin
npm install
npm run dev

# Client Frontend (в іншому терміналі)
cd client
npm install
npm run dev
```

### Доступ до сервісів

Після запуску всі сервіси будуть доступні:

| Сервіс | URL | Опис |
|--------|-----|------|
| **Admin Frontend** | http://localhost:5173 | Адмін панель |
| **Client Frontend** | http://localhost:5174 | Клієнтський інтерфейс |
| **Auth Service API** | http://localhost:8001 | Аутентифікація |
| **Auth Service Docs** | http://localhost:8001/docs | Swagger документація |
| **Catalog Service API** | http://localhost:8002 | Каталог товарів |
| **Catalog Service Docs** | http://localhost:8002/docs | Swagger документація |
| **Order Service API** | http://localhost:8003 | Замовлення та кошик |
| **Order Service Docs** | http://localhost:8003/docs | Swagger документація |

### Default користувачі

Після першого запуску створюються тестові користувачі:

| Username | Password | Role | Опис |
|----------|----------|------|------|
| `admin` | `admin` | SYSTEM_ADMIN | Повний доступ до всіх функцій |
| `manager` | `manager` | MANAGER | Управління товарами та замовленнями |
| `client` | `client` | CLIENT | Звичайний користувач |

**Важливо:** Для production змініть паролі за замовчуванням!

## Docker

### Запуск з Docker Compose

Найпростіший спосіб запустити весь проект:

```bash
# Зібрати та запустити всі сервіси
docker-compose up --build

# Запуск в фоновому режимі
docker-compose up -d --build

# Перегляд логів
docker-compose logs -f

# Перегляд логів конкретного сервісу
docker-compose logs -f auth-service

# Зупинка
docker-compose down

# Зупинка з видаленням volumes (очищення БД)
docker-compose down -v
```

### Dockerfile для кожного сервісу

Кожен сервіс має свій Dockerfile:

- `services/auth-service/Dockerfile`
- `services/catalog-service/Dockerfile`
- `services/order-service/Dockerfile`
- `admin/Dockerfile`
- `client/Dockerfile`

### Збірка окремих образів

```bash
# Auth Service
docker build -t auth-service:latest ./services/auth-service

# Catalog Service
docker build -t catalog-service:latest ./services/catalog-service

# Order Service
docker build -t order-service:latest ./services/order-service

# Admin Frontend
docker build -t admin-frontend:latest ./admin

# Client Frontend
docker build -t client-frontend:latest ./client
```

Детальна інструкція: [DOCKER.md](DOCKER.md)

## Kubernetes Deployment

### Вимоги

- Kubernetes кластер (minikube, k3s, kind, або cloud кластер: GKE, EKS, AKS)
- `kubectl` встановлений та налаштований
- Docker images зібрані та доступні (локально або в registry)

### Швидкий старт з minikube (локальний кластер)

**Увага:** Локальний minikube працює тільки для локальної розробки. Для автоматичного деплою через GitHub Actions потрібен публічний кластер.

#### 1. Запустити minikube

```bash
# Запустити minikube
minikube start

# Перевірити статус
minikube status

# Перевірити kubectl
kubectl cluster-info
```

#### 2. Налаштувати Docker для minikube

```bash
# Налаштувати Docker для використання minikube registry
eval $(minikube docker-env)  # Linux/macOS
# Або для PowerShell:
minikube docker-env | Invoke-Expression  # Windows PowerShell
```

#### 3. Зібрати Docker images

```bash
# Повернутися в корінь проекту
cd /path/to/ippt-microservices

# Зібрати всі образи
docker build -t auth-service:latest ./services/auth-service
docker build -t catalog-service:latest ./services/catalog-service
docker build -t order-service:latest ./services/order-service
docker build -t client-frontend:latest ./client
docker build -t admin-frontend:latest ./admin
```

#### 4. Деплой в Kubernetes

```bash
# Створити namespace
kubectl apply -f k8s/namespace.yaml

# Застосувати конфігурацію
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Застосувати backend сервіси
kubectl apply -f k8s/auth-service/
kubectl apply -f k8s/catalog-service/
kubectl apply -f k8s/order-service/

# Застосувати frontend сервіси
kubectl apply -f k8s/client-frontend/
kubectl apply -f k8s/admin-frontend/

# Застосувати Ingress (опціонально)
kubectl apply -f k8s/ingress.yaml
```

#### 5. Перевірка статусу

```bash
# Перевірити pods
kubectl get pods -n ippt-microservices

# Перевірити services
kubectl get svc -n ippt-microservices

# Перевірити deployments
kubectl get deployments -n ippt-microservices

# Переглянути логи
kubectl logs -f deployment/auth-service -n ippt-microservices
```

#### 6. Доступ до сервісів

```bash
# Для minikube - отримати URL
minikube service list -n ippt-microservices

# Або прокси для локального доступу
kubectl port-forward svc/auth-service 8001:8001 -n ippt-microservices
kubectl port-forward svc/catalog-service 8002:8002 -n ippt-microservices
kubectl port-forward svc/order-service 8003:8003 -n ippt-microservices
```

### Деплой в Cloud кластер (GKE, EKS, AKS)

#### Google Kubernetes Engine (GKE)

```bash
# 1. Налаштувати gcloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Створити кластер (якщо немає)
gcloud container clusters create ippt-cluster \
  --zone europe-west1-b \
  --num-nodes 2 \
  --machine-type e2-medium

# 3. Отримати credentials
gcloud container clusters get-credentials ippt-cluster --zone europe-west1-b

# 4. Зібрати та запушити образи в GCR або Artifact Registry
# (оновіть image paths в k8s/*/deployment.yaml)

# 5. Застосувати manifests
kubectl apply -f k8s/
```

#### Amazon EKS

```bash
# 1. Налаштувати AWS CLI
aws configure

# 2. Створити кластер (якщо немає)
eksctl create cluster --name ippt-cluster --region us-east-1 --node-type t3.medium --nodes 2

# 3. Оновити image paths в k8s/*/deployment.yaml на ECR URLs

# 4. Застосувати manifests
kubectl apply -f k8s/
```

#### Azure Kubernetes Service (AKS)

```bash
# 1. Налаштувати Azure CLI
az login

# 2. Створити кластер (якщо немає)
az aks create --resource-group ippt-rg --name ippt-cluster --node-count 2 --node-vm-size Standard_B2s

# 3. Отримати credentials
az aks get-credentials --resource-group ippt-rg --name ippt-cluster

# 4. Оновити image paths в k8s/*/deployment.yaml на ACR URLs

# 5. Застосувати manifests
kubectl apply -f k8s/
```

### Kubernetes Компоненти

Проект використовує наступні Kubernetes ресурси:

- **Namespace**: `ippt-microservices` - ізоляція ресурсів
- **Deployment** - 2 replicas для кожного сервісу (висока доступність)
- **Service** - ClusterIP для внутрішньої комунікації між сервісами
- **ConfigMap** - конфігурація сервісів (URLs, налаштування)
- **Secret** - JWT ключі та інші секрети
- **Ingress** - маршрутизація зовнішнього трафіку (опціонально)
- **Health Checks** - liveness та readiness probes для автоматичного перезапуску

### Автоматичний деплой через GitHub Actions

Після налаштування `KUBECONFIG` secret в GitHub, кожен push в `main` гілку автоматично:
1. Збере образи
2. Запушить в GitHub Container Registry
3. Задеплоїть в Kubernetes кластер

Детальна інструкція: [docs/KUBERNETES_SETUP.md](docs/KUBERNETES_SETUP.md)

## CI/CD

### GitHub Actions Pipeline

Проект має повний CI/CD pipeline в `.github/workflows/ci-cd.yml`:

#### Етапи pipeline (послідовно):

```
┌─────────┐
│  Lint   │ → Перевірка якості коду (flake8 для Python, eslint для Frontend)
└─────────┘
    │
    ↓
┌─────────┐
│  Tests  │ → Unit tests для Python сервісів (pytest, coverage >= 70%)
└─────────┘
    │
    ↓
┌──────────────┐
│ Build Images │ → Збірка Docker образів для всіх сервісів
└──────────────┘
    │
    ↓
┌─────────────┐
│ Push Images │ → Завантаження до GitHub Container Registry
└─────────────┘
    │
    ↓
┌─────────────────┐
│ Deploy to K8s   │ → Автоматичний деплой (якщо налаштовано KUBECONFIG)
└─────────────────┘
```

#### Детальний опис етапів

1. **Lint** ✅
   - Python сервіси: `flake8` для auth-service, catalog-service, order-service
   - Frontend сервіси: `eslint` для client-frontend, admin-frontend
   - Перевірка синтаксису та стилю коду
   - Non-blocking (lint помилки не зупиняють pipeline)

2. **Tests** ✅
   - Unit tests для всіх Python сервісів (pytest)
   - Покриття коду >= 70% (обов'язково для auth-service та catalog-service)
   - Покриття коду >= 60% (для order-service через складні code paths)
   - Тестування на Python 3.11, 3.12, 3.13
   - Coverage reports завантажуються до Codecov

3. **Build Docker Images** ✅
   - Збірка образів для всіх сервісів паралельно
   - Використання Docker Buildx з кешуванням
   - Multi-stage builds для оптимізації розміру

4. **Push to Registry** ✅
   - Завантаження до GitHub Container Registry (ghcr.io)
   - Теги: `latest`, `{branch}`, `{sha}`, семантичні версії
   - **Registry:** `ghcr.io/ВАШ_GITHUB_USERNAME/ippt-microservices-{service-name}`

5. **Deploy to Kubernetes** ✅ (опціонально)
   - Автоматичний деплой в кластер (тільки main branch)
   - Оновлення image tags в deployment файлах
   - Застосування всіх Kubernetes ресурсів
   - Очікування готовності deployments

**Сервіси:**
- **Backend:** auth-service, catalog-service, order-service
- **Frontend:** client-frontend, admin-frontend

#### Налаштування автоматичного деплою

Щоб увімкнути автоматичний деплой:

1. **Додати secret `KUBECONFIG` в GitHub:**
   - Перейдіть: **Settings** → **Secrets and variables** → **Actions**
   - Натисніть **New repository secret**
   - **Name**: `KUBECONFIG`
   - **Secret**: base64 закодований kubeconfig файл
   - Детальна інструкція: [docs/KUBERNETES_SETUP.md](docs/KUBERNETES_SETUP.md)

2. **Оновити image paths в Kubernetes manifests:**
   - Відредагувати `k8s/*/deployment.yaml` файли
   - Замінити `ghcr.io/YOUR_GITHUB_USERNAME/...` на `ghcr.io/ВАШ_GITHUB_USERNAME/...`

**Без налаштування KUBECONFIG:**
Pipeline автоматично пропустить крок деплою, але всі інші етапи (Lint → Tests → Build → Push) виконаються.

## Тестування

### Unit Tests

Проект містить комплексні unit tests для всіх Python сервісів:

- **auth-service**: Coverage ~95% (76 тестів)
- **catalog-service**: Coverage ~82% (29 тестів)
- **order-service**: Coverage ~65% (33 тести)

Всі тести включають перевірку:
- Security functions (hash_password, verify_password, JWT)
- API endpoints (CRUD операції)
- Dependencies (get_current_user, require_roles)
- Database models

### Структура тестів

Кожен Python сервіс має свою директорію тестів:

```
services/{service}/backend/tests/
├── conftest.py              # Pytest fixtures (test DB, clients, mocks)
├── test_security.py         # Security functions tests
├── test_models.py           # Models tests
├── test_deps.py             # Dependencies tests
├── test_*.py                # Endpoint tests
└── ...
```

### Запуск тестів локально

```bash
# Auth Service
cd services/auth-service
pytest backend/tests/ -v --cov=backend --cov-report=term-missing --cov-fail-under=70

# Catalog Service
cd services/catalog-service
pytest backend/tests/ -v --cov=backend --cov-report=term-missing --cov-fail-under=70

# Order Service
cd services/order-service
pytest backend/tests/ -v --cov=backend --cov-report=term-missing --cov-fail-under=60
```

### Перегляд coverage report

Після запуску тестів, HTML звіт генерується в `htmlcov/`:

```bash
# Відкрити в браузері
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

## API Документація

Кожен сервіс має автоматичну OpenAPI/Swagger документацію:

- **Auth Service**: http://localhost:8001/docs
- **Catalog Service**: http://localhost:8002/docs
- **Order Service**: http://localhost:8003/docs

Документація містить:
- Опис всіх endpoints
- Параметри запитів та відповідей
- Можливість тестування API прямо в браузері

## Troubleshooting

### Проблеми з Docker

**Помилка: "Cannot connect to Docker daemon"**
```bash
# Перевірити що Docker Desktop запущений
# Windows: запустити Docker Desktop
# Linux: sudo systemctl start docker
```

**Помилка: "Port already in use"**
```bash
# Знайти процес що використовує порт
# Windows:
netstat -ano | findstr :8001

# Linux/macOS:
lsof -i :8001

# Зупинити процес або змінити порт в docker-compose.yml
```

### Проблеми з Python залежностями

**Помилка: "ModuleNotFoundError"**
```bash
# Переконатися що PYTHONPATH встановлено правильно
# Windows:
set PYTHONPATH=%CD%

# Linux/macOS:
export PYTHONPATH=$(pwd)
```

### Проблеми з Node.js

**Помилка: "npm install failed"**
```bash
# Очистити cache та перевстановити
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Проблеми з Kubernetes

**Помилка: "ImagePullBackOff"**
```bash
# Перевірити що образи зібрані та доступні
kubectl describe pod <pod-name> -n ippt-microservices

# Для minikube - переконатися що використовується minikube registry
eval $(minikube docker-env)
```

**Помилка: "Connection refused"**
```bash
# Перевірити що сервіси працюють
kubectl get pods -n ippt-microservices
kubectl logs <pod-name> -n ippt-microservices
```

## Корисні посилання

- **GitHub Repository**: https://github.com/YOUR_GITHUB_USERNAME/ippt-microservices
- **Docker документація**: [DOCKER.md](DOCKER.md)
- **Kubernetes setup**: [docs/KUBERNETES_SETUP.md](docs/KUBERNETES_SETUP.md)
- **FastAPI документація**: https://fastapi.tiangolo.com/
- **React документація**: https://react.dev/
- **Kubernetes документація**: https://kubernetes.io/docs/

