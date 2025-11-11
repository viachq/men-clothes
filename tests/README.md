# 🧪 Backend Tests

Комплексний набір юніт-тестів для backend частини проєкту Food Delivery.

## 📊 Результати

✅ **66 тестів проходять успішно**  
📈 **61% покриття коду backend**

## 🏗️ Структура

```
tests/
├── conftest.py           # Shared fixtures and test configuration
├── unit/                 # Unit tests (isolated, no external dependencies)
│   └── test_security.py  # Password hashing & JWT token tests (26 tests)
└── integration/          # Integration tests (with database and API)
    ├── test_auth.py      # Authentication flow tests (17 tests)
    ├── test_cart.py      # Shopping cart tests (11 tests)
    └── test_menu.py      # Menu & categories tests (12 tests)
```

## 🚀 Запуск тестів

```bash
# Всі тести
$env:PYTHONPATH="$PWD"; uv run pytest tests/ -v

# Тільки unit тести
$env:PYTHONPATH="$PWD"; uv run pytest tests/unit/ -v

# Тільки integration тести
$env:PYTHONPATH="$PWD"; uv run pytest tests/integration/ -v

# З покриттям коду
$env:PYTHONPATH="$PWD"; uv run pytest tests/ --cov=backend --cov-report=html

# Конкретний файл
$env:PYTHONPATH="$PWD"; uv run pytest tests/unit/test_security.py -v

# Конкретний тест
$env:PYTHONPATH="$PWD"; uv run pytest tests/unit/test_security.py::TestPasswordHashing::test_hash_password_creates_hash -v
```

## 📦 Покриття модулів

| Модуль | Coverage | Тести |
|--------|----------|-------|
| **security.py** | 93% | ✅ 26 |
| **auth (login/register)** | 100% | ✅ 17 |
| **cart.py** | 100% | ✅ 11 |
| **menu.py** | 91% | ✅ 6 |
| **categories.py** | 94% | ✅ 6 |
| **admin роутери** | 38-86% | ⚠️ Частково |
| **models** | 100% | ✅ Непрямо |

## 🧪 Що тестується

### Security (26 тестів)
- ✅ Хешування паролів з різними форматами
- ✅ Верифікація правильних/неправильних паролів
- ✅ Створення та валідація JWT токенів
- ✅ Обробка підроблених токенів
- ✅ Час закінчення токенів

### Authentication (17 тестів)
- ✅ Реєстрація нових користувачів
- ✅ Валідація username (дублікати, порожні значення)
- ✅ Логін з правильними/неправильними credentials
- ✅ Доступ до захищених endpoint
- ✅ Role-based access control (client vs admin)

### Cart (11 тестів)
- ✅ CRUD операції з кошиком
- ✅ Додавання/видалення/оновлення товарів
- ✅ Автоматичне створення кошика
- ✅ Ізоляція кошиків між користувачами
- ✅ Вимога автентифікації

### Menu & Categories (12 тестів)
- ✅ Публічний доступ до меню
- ✅ Фільтрація по категоріям
- ✅ Admin CRUD операції
- ✅ Перевірка прав доступу (client vs admin)

## 🎯 Майбутні тести (TODO)

- [ ] Order creation and status updates
- [ ] Payment processing
- [ ] Reviews CRUD
- [ ] Admin stats endpoints
- [ ] User management
- [ ] Restaurant info management

## 💡 Приклади використання

```python
# Приклад тесту
def test_example(client, auth_headers):
    """Example test with authenticated user."""
    response = client.get("/cart/me", headers=auth_headers)
    assert response.status_code == 200
    assert "items" in response.json()
```

## 📝 Нотатки

- Використовується **SQLite in-memory** база для швидкості
- **StaticPool** забезпечує спільне з'єднання для всіх тестів
- Кожен тест отримує **чисту базу даних**
- Фікстури автоматично створюють тестових користувачів, меню, категорії

