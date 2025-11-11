# 🍕 Food Delivery System

Повнофункціональна система замовлення їжі з адмін-панеллю та клієнтським сайтом.

## 📁 Структура проєкту

```
ippt_project/
├── backend/       # FastAPI сервер (Python) - порт 8000
├── admin/         # Адмін-панель (React + TS) - порт 5173
├── client/        # Клієнтський сайт (React + TS) - порт 5174
└── app.db         # База даних SQLite
```

## 🚀 Швидкий старт

### Автоматичний запуск (Windows)

Подвійний клік на `start-all.bat` - запустить всі 3 сервіси одночасно!

```cmd
start-all.bat
```

### Ручний запуск

**Backend:**
```cmd
cd E:\ippt\ippt_project
uv run uvicorn backend.main:app --reload
```

**Admin Panel:**
```cmd
cd E:\ippt\ippt_project\admin
npm run dev
```

**Client Site:**
```cmd
cd E:\ippt\ippt_project\client
npm run dev
```

## 🌐 URLs

- **Client Site**: http://localhost:5174 - для клієнтів
- **Admin Panel**: http://localhost:5173 - для адміністраторів
- **Backend API**: http://localhost:8000/docs - Swagger документація

## 👤 Credentials

### Admin Panel
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `system_admin`

### Client Site
- Реєстрація доступна на сайті
- Нові користувачі автоматично отримують роль `client`

## 🤖 Telegram Bot

**Push-сповіщення про нові замовлення!**
- 🔔 Миттєві сповіщення адміністраторам
- 📊 Детальна інформація: сума, адреса, товари
- ✅ Все налаштовано в `backend/core/config.py`

## ✨ Функціонал

### 🌐 Клієнтський сайт (Client)

#### Для всіх користувачів:
- 🍕 **Перегляд меню** - з фільтром по категоріях
- 🔍 **Категорії** - Перші страви, Десерти, тощо

#### Для авторизованих користувачів:
- 🛒 **Кошик**:
  - Додавання страв (автоматично + / -)
  - Зміна кількості
  - Видалення товарів
  - Очистити весь кошик
  - Підрахунок загальної суми
  
- 📦 **Оформлення замовлення**:
  - Обов'язкова адреса доставки
  - Опційна дата/час доставки (планування на майбутнє)
  - Оплата тільки карткою
  
- 📋 **Історія замовлень**:
  - Перегляд всіх замовлень
  - Відстеження статусу в реальному часі
  - Адреса та час доставки
  
- ⭐ **Відгуки**:
  - Оцінка 1-5 зірок
  - Текстовий коментар (мін. 10 символів)
  - Тільки для доставлених замовлень

### 🔧 Адмін-панель (Admin)

#### System Admin + Restaurant Admin:
- 📊 **Dashboard**:
  - Статистика замовлень
  - Дохід
  - Top страви
  
- 📦 **Управління замовленнями**:
  - Перегляд всіх замовлень
  - Деталі з items
  - Зміна статусу (pending → accepted → preparing → ready → delivering → delivered)
  - Фільтр по статусу
  
- 🍕 **Управління меню**:
  - Додати нову страву
  - Редагувати існуючу
  - Видалити страву
  - Призначити категорію
  - Додати зображення (URL)
  - Ціна в копійках (для точності)
  
- 📁 **Категорії**:
  - Створити категорію
  - Редагувати назву/опис
  - Видалити категорію
  
- 🏪 **Інформація про ресторан**:
  - Назва
  - Опис
  - Адреса
  - Телефон
  - Години роботи
  
- ⭐ **Модерація відгуків**:
  - Перегляд всіх відгуків
  - Видалення неприйнятних відгуків

#### Тільки System Admin:
- 👥 **Управління користувачами**:
  - Перегляд всіх користувачів
  - Призначення ролей (client / restaurant_admin / system_admin)

## 🛡️ Безпека

### Backend:
- ✅ JWT токени для автентифікації
- ✅ Хешування паролів з salt (SHA256)
- ✅ CORS налаштовано
- ✅ Role-based access control
- ✅ Захищені ендпоінти кошика (тільки свій)
- ✅ Валідація всіх даних через Pydantic

### Frontend:
- ✅ **Admin Panel**: блокування входу для role=client
- ✅ **Client Site**: захист приватних сторінок (cart, orders, checkout)
- ✅ Автоматичний logout при 401
- ✅ Збереження токенів в localStorage

## 🔒 Ролі користувачів

| Роль | Доступ | Можливості |
|------|--------|------------|
| **client** | ❌ Admin Panel<br>✅ Client Site | Замовляти, переглядати меню, залишати відгуки |
| **restaurant_admin** | ✅ Admin Panel<br>❌ Client Site | Управління замовленнями, меню, рестораном, відгуками |
| **system_admin** | ✅ Admin Panel<br>❌ Client Site | Все + управління користувачами та призначення адмінів |

## 🛠️ Технології

### Backend
- Python 3.14
- FastAPI
- SQLAlchemy
- SQLite
- JWT (python-jose)
- Pydantic
- Uvicorn
- aiogram (Telegram Bot)

### Frontend (Admin + Client)
- React 18
- TypeScript
- Vite
- TailwindCSS v3
- React Router v7
- Axios
- Lucide Icons

## 📋 API Endpoints

### Auth
- `POST /auth/register` - Реєстрація (тільки client)
- `POST /auth/login` - Вхід (повертає роль)

### Menu
- `GET /menu/` - Список страв (фільтр: ?category_id=1)
- `GET /menu/{id}` - Деталі страви

### Categories
- `GET /categories/` - Всі категорії
- `POST /admin/categories` - Створити (admin only)
- `PUT /admin/categories/{id}` - Редагувати (admin only)
- `DELETE /admin/categories/{id}` - Видалити (admin only)

### Cart
- `GET /cart/me` - Мій кошик
- `POST /cart/me/items` - Додати товар
- `PUT /cart/me/items/{id}` - Змінити кількість
- `DELETE /cart/me/items/{id}` - Видалити товар
- `DELETE /cart/me` - Очистити кошик

### Orders
- `POST /orders` - Створити замовлення
- `GET /orders` - Мої замовлення
- `GET /orders/{id}` - Деталі замовлення
- `POST /orders/{id}/review` - Залишити відгук
- `GET /admin/orders` - Всі замовлення (admin only)
- `GET /admin/orders/{id}` - Деталі з items (admin only)
- `PUT /admin/orders/{id}/status` - Змінити статус (admin only)

### Reviews
- `GET /reviews/` - Всі відгуки
- `DELETE /reviews/{id}` - Видалити (admin or owner)

### Users
- `GET /admin/users/` - Всі користувачі (system_admin only)
- `PUT /admin/users/{id}/role` - Змінити роль (system_admin only)

### Restaurant
- `GET /restaurant/info` - Інформація
- `PUT /admin/restaurant` - Редагувати (admin only)

## 🎯 Use Cases Покриття

✅ **100% покриття** всіх use cases з UML діаграми:

### Клієнт:
1. ✅ Авторизація (username/password)
2. ✅ Реєстрація
3. ✅ Перегляд меню з категоріями
4. ✅ Додавання в кошик
5. ✅ Перегляд ТІЛЬКИ свого кошика
6. ✅ Редагування кошика (кількість, видалення)
7. ✅ Оформлення (тільки якщо кошик не пустий)
8. ✅ Адреса доставки (обов'язкова)
9. ✅ Дата замовлення (опційна, планування)
10. ✅ Оплата ТІЛЬКИ карткою
11. ✅ Історія замовлень
12. ✅ Відстеження статусу
13. ✅ Відгуки на доставлені замовлення

### System Admin:
14. ✅ Призначення адміністраторів ресторану

### Restaurant Admin + System Admin:
15. ✅ Перегляд замовлень
16. ✅ Деталі замовлення з items
17. ✅ Зміна статусу
18. ✅ Статистика
19. ✅ Видалення відгуків
20. ✅ Редагування інформації про ресторан (назва, опис, адреса, телефон, години)
21. ✅ Управління меню (додати/редагувати/видалити)
22. ✅ Управління категоріями

## 📱 Screenshots

### Client Site (localhost:5174)
- Головна з меню та фільтрами категорій
- Кошик з товарами
- Оформлення замовлення
- Історія замовлень

### Admin Panel (localhost:5173)
- Dashboard зі статистикою
- Управління замовленнями
- Управління меню та категоріями
- Налаштування ресторану

## 🔧 Розробка

### Встановлення

**Backend:**
```bash
cd backend
# uv автоматично встановить залежності з pyproject.toml
```

**Admin:**
```bash
cd admin
npm install
```

**Client:**
```bash
cd client
npm install
```

### Структура бази даних

- `users` - Користувачі з ролями
- `categories` - Категорії страв
- `menu_items` - Страви (з category_id)
- `carts` - Кошики користувачів
- `cart_items` - Товари в кошику
- `orders` - Замовлення
- `order_items` - Страви в замовленні
- `reviews` - Відгуки (один на замовлення)
- `payments` - Платежі
- `restaurant_info` - Інформація про ресторан

## 🎓 Проєкт для ІППТ

Розроблено з ❤️ для курсу ІППТ (Інженерія програмного продукту та технології)

### Використані паттерни та практики:
- Clean Architecture
- Repository Pattern
- Dependency Injection
- Role-Based Access Control (RBAC)
- RESTful API
- Type Safety (TypeScript + Pydantic)
- Responsive Design
- Component-Based Architecture
