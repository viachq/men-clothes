# CI/CD Pipeline Documentation

## Огляд

Цей CI/CD pipeline автоматизує процес розробки, тестування, збірки та деплою мікросервісного застосунку Food Delivery.

## Структура Pipeline

Pipeline складається з 4 основних етапів:

```
┌─────────┐
│  LINT   │ → Перевірка якості коду
└────┬────┘
     │
┌────▼────┐
│  TEST   │ → Запуск тестів (якщо є)
└────┬────┘
     │
┌────▼────┐
│  BUILD  │ → Збірка Docker образів
└────┬────┘
     │
┌────▼────┐
│ DEPLOY  │ → Деплой в Kubernetes
└─────────┘
```

## Етапи Pipeline

### 1. LINT (Перевірка коду)

**Мета:** Перевірити якість коду перед збіркою

**Що робить:**
- Перевіряє Python код за допомогою `flake8` (синтаксичні помилки)
- Перевіряє форматування за допомогою `black`
- Перевіряє Frontend код за допомогою ESLint (якщо налаштовано)

**Якщо не пройдено:** Pipeline зупиняється, збірка не відбувається

**Тривалість:** ~2-3 хвилини

---

### 2. TEST (Тестування)

**Мета:** Запустити unit тести та перевірити coverage

**Що робить:**
- Встановлює pytest та інші тестові інструменти
- Шукає тести в `services/*/backend/tests/`
- Запускає тести для кожного сервісу
- Генерує звіт про coverage

**Особливості:**
- Якщо тестів немає — етап пропускається (не блокує pipeline)
- Якщо тести є — вони обов'язково запускаються

**Тривалість:** ~3-5 хвилин (залежить від кількості тестів)

---

### 3. BUILD (Збірка Docker образів)

**Мета:** Зібрати та опублікувати Docker образи всіх сервісів

**Що робить:**
- Збирає Docker образи для 5 сервісів:
  - `auth-service`
  - `catalog-service`
  - `order-service`
  - `client-frontend`
  - `admin-frontend`
- Створює теги для образів:
  - `latest` — для main гілки
  - `main-<sha>` — з SHA коміту
  - `develop-<sha>` — для develop гілки
- Публікує образи в **GitHub Container Registry** (`ghcr.io`)

**Результат:** Образі доступні за адресою:
```
ghcr.io/<username>/food-delivery-auth-service:latest
ghcr.io/<username>/food-delivery-catalog-service:latest
ghcr.io/<username>/food-delivery-order-service:latest
ghcr.io/<username>/food-delivery-client-frontend:latest
ghcr.io/<username>/food-delivery-admin-frontend:latest
```

**Тривалість:** ~5-10 хвилин (паралельно для всіх сервісів)

---

### 4. DEPLOY (Деплой в Kubernetes)

**Мета:** Автоматично розгорнути новий код в Kubernetes кластер

**Коли запускається:**
- ✅ Тільки при **push** в гілки `main` або `develop`
- ❌ НЕ запускається для Pull Requests

**Що робить:**
1. Встановлює `kubectl` та налаштовує підключення до кластера
2. Оновлює Kubernetes manifests з новими тегами образів
3. Застосовує зміни в кластер:
   - Namespace
   - ConfigMap та Secret
   - Deployments та Services для всіх сервісів
4. Чекає, поки поді стануть Ready (до 5 хвилин)
5. Перевіряє статус deployment

**Тривалість:** ~5-10 хвилин

---

## Коли запускається Pipeline

Pipeline автоматично запускається:

### ✅ При Push
- Push в гілку `main` → запускається всі етапи (включно з DEPLOY)
- Push в гілку `develop` → запускається всі етапи (включно з DEPLOY)
- Push в інші гілки → НЕ запускається

### ✅ При Pull Request
- PR в `main` → запускається LINT, TEST, BUILD (без DEPLOY)
- PR в `develop` → запускається LINT, TEST, BUILD (без DEPLOY)

### ❌ Не запускається
- Push в feature гілки
- Push в інші гілки (окрім main/develop)

---

## Налаштування

### Обов'язкові Secrets

Для роботи DEPLOY етапу потрібно налаштувати:

#### 1. KUBECONFIG Secret

**Як створити:**
```bash
# Отримати kubeconfig з вашого кластера
kubectl config view --flatten > kubeconfig.yaml

# Закодувати в base64
cat kubeconfig.yaml | base64 -w 0
```

**Як додати в GitHub:**
1. Перейти в Settings → Secrets and variables → Actions
2. Створити новий secret з назвою `KUBECONFIG`
3. Вставити закодований kubeconfig

### Опціональні налаштування

#### Зміна реєстру образів

За замовчуванням використовується `ghcr.io`. Щоб змінити:

```yaml
env:
  REGISTRY: docker.io  # або інший registry
  IMAGE_PREFIX: your-org/food-delivery
```

#### Додавання нових гілок

Щоб додати інші гілки для деплою:

```yaml
on:
  push:
    branches: [ main, develop, staging ]  # додати staging
```

---

## Перевірка статусу

### В GitHub

1. Перейти в репозиторій
2. Вкладка **Actions**
3. Вибрати workflow **CI/CD Pipeline**
4. Подивитися статус останнього запуску

### В терміналі

```bash
# Перевірити статус останнього workflow
gh run list --workflow=ci-cd.yml

# Подивитися логи
gh run view <run-id> --log
```

---

## Troubleshooting

### Pipeline не запускається

**Проблема:** Push в GitHub, але pipeline не запускається

**Рішення:**
1. Перевірити, що файл `.github/workflows/ci-cd.yml` існує
2. Перевірити, що гілка `main` або `develop`
3. Перевірити, що GitHub Actions увімкнені в Settings → Actions

---

### LINT етап падає

**Проблема:** `flake8` знаходить помилки

**Рішення:**
```bash
# Виправити помилки локально
flake8 services/auth-service/backend
black services/auth-service/backend  # автоматично виправить форматування
```

---

### BUILD етап падає

**Проблема:** Docker образ не збирається

**Рішення:**
1. Перевірити, що Dockerfile існує для сервісу
2. Перевірити логи в GitHub Actions
3. Спробувати зібрати локально:
   ```bash
   docker build -t test ./services/auth-service
   ```

---

### DEPLOY етап падає

**Проблема:** Не вдається підключитися до Kubernetes

**Рішення:**
1. Перевірити, що secret `KUBECONFIG` налаштований
2. Перевірити, що кластер доступний
3. Перевірити права доступу в kubeconfig

**Проблема:** Поді не стають Ready

**Рішення:**
```bash
# Перевірити логи подів
kubectl logs -n food-delivery deployment/auth-service

# Перевірити поді
kubectl get pods -n food-delivery

# Перевірити events
kubectl get events -n food-delivery --sort-by='.lastTimestamp'
```

---

## Локальне тестування

### Тестування LINT

```bash
# Встановити інструменти
pip install flake8 black

# Перевірити код
flake8 services/auth-service/backend
black --check services/auth-service/backend
```

### Тестування BUILD

```bash
# Зібрати образ локально
docker build -t auth-service:test ./services/auth-service

# Перевірити, що образ працює
docker run -p 8001:8001 auth-service:test
```

### Тестування DEPLOY

```bash
# Застосувати manifests локально
cd k8s
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f auth-service/
```

---

## Додаткові ресурси

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Kubernetes Deployment Guide](./../../k8s/README.md)

---

## Підтримка

Якщо виникли проблеми:
1. Перевірте логи в GitHub Actions
2. Перевірте цей README
3. Створіть Issue в репозиторії
