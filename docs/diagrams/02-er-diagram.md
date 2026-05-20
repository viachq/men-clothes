# ER-діаграма (схема баз даних)

Кожен мікросервіс має власну базу. Зв'язки між сервісами — логічні (через
`user_id`, `menu_item_id`), фізичних зовнішніх ключів між базами немає
(особливість мікросервісної архітектури — database-per-service).

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string email UK
        string phone
        string name
        string password "bcrypt-хеш"
        string role "client|manager|system_admin"
        bool is_active
        bool is_verified
        string verification_token UK
        datetime token_expires_at
        datetime created_at
    }

    CATEGORIES {
        int id PK
        string name
    }
    MENU_ITEMS {
        int id PK
        int category_id FK
        string name
        text description
        int price "копійки"
        string image_url
    }
    PRODUCT_VARIANTS {
        int id PK
        int menu_item_id FK
        string size "S|M|L|XL"
        int stock
    }
    PRODUCT_REVIEWS {
        int id PK
        int product_id FK
        int user_id "лог. зв'язок з USERS"
        string username
        int rating "1..5"
        text comment
        datetime created_at
    }

    CARTS {
        int id PK
        int user_id UK "лог. зв'язок з USERS"
    }
    CART_ITEMS {
        int id PK
        int cart_id FK
        int menu_item_id "лог. зв'язок з MENU_ITEMS"
        int quantity
        int price
    }
    ORDERS {
        int id PK
        int user_id "лог. зв'язок з USERS"
        string status "pending|delivering|delivered|cancelled"
        datetime created_at
        datetime updated_at
        string delivery_address
        string payment_method
        int total_price "копійки"
        datetime delivery_time
        string promo_code
        int discount "копійки"
    }
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int menu_item_id "лог. зв'язок з MENU_ITEMS"
        int quantity
        int price
    }
    PAYMENTS {
        int id PK
        int order_id FK,UK
        int amount
        string status "pending|completed|failed|refunded"
        string transaction_id UK
        datetime created_at
        datetime updated_at
    }
    PROMO_CODES {
        int id PK
        string code UK
        int discount_percent
        int discount_amount
        int min_order_amount
        int max_uses
        int current_uses
        bool is_active
        datetime valid_from
        datetime valid_until
        datetime created_at
    }

    CATEGORIES ||--o{ MENU_ITEMS : "містить"
    MENU_ITEMS ||--o{ PRODUCT_VARIANTS : "має розміри"
    MENU_ITEMS ||--o{ PRODUCT_REVIEWS : "має відгуки"
    CARTS ||--o{ CART_ITEMS : "містить"
    ORDERS ||--o{ ORDER_ITEMS : "містить"
    ORDERS ||--|| PAYMENTS : "має оплату"
    USERS ||..o{ ORDERS : "оформлює (лог.)"
    USERS ||..o{ PRODUCT_REVIEWS : "залишає (лог.)"
    USERS ||..|| CARTS : "має кошик (лог.)"
    PROMO_CODES ||..o{ ORDERS : "застосовується (лог.)"
```

**Примітка.** Пунктирні зв'язки (`..`) — логічні (cross-service): сутності
знаходяться в різних базах даних різних мікросервісів і пов'язані лише
ідентифікаторами, без фізичних FOREIGN KEY. Суцільні (`--`) — фізичні зовнішні
ключі в межах однієї бази.

Грошові суми зберігаються в копійках (ціле число) для уникнення похибок
обчислень із плаваючою комою.
