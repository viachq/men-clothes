# Діаграма класів (доменна модель)

Класи моделей предметної області (SQLAlchemy ORM), згруповані за мікросервісами.

```mermaid
classDiagram
    class User {
        +int id
        +str username
        +str email
        +str phone
        +str name
        -str password
        +str role
        +bool is_active
        +bool is_verified
        +str verification_token
        +datetime token_expires_at
        +datetime created_at
    }

    class Category {
        +int id
        +str name
    }
    class MenuItem {
        +int id
        +int category_id
        +str name
        +str description
        +int price
        +str image_url
    }
    class ProductVariant {
        +int id
        +int menu_item_id
        +str size
        +int stock
    }
    class ProductReview {
        +int id
        +int product_id
        +int user_id
        +str username
        +int rating
        +str comment
        +datetime created_at
    }

    class Cart {
        +int id
        +int user_id
    }
    class CartItem {
        +int id
        +int cart_id
        +int menu_item_id
        +int quantity
        +int price
    }
    class Order {
        +int id
        +int user_id
        +str status
        +str delivery_address
        +str payment_method
        +int total_price
        +str promo_code
        +int discount
        +datetime delivery_time
        +datetime created_at
    }
    class OrderItem {
        +int id
        +int order_id
        +int menu_item_id
        +int quantity
        +int price
    }
    class Payment {
        +int id
        +int order_id
        +int amount
        +str status
        +str transaction_id
        +datetime created_at
    }
    class PromoCode {
        +int id
        +str code
        +int discount_percent
        +int discount_amount
        +int min_order_amount
        +int max_uses
        +int current_uses
        +bool is_active
        +datetime valid_from
        +datetime valid_until
    }

    Category "1" --> "*" MenuItem
    MenuItem "1" --> "*" ProductVariant
    MenuItem "1" --> "*" ProductReview
    Cart "1" --> "*" CartItem
    Order "1" --> "*" OrderItem
    Order "1" --> "1" Payment
    User ..> Order : user_id
    User ..> Cart : user_id
    User ..> ProductReview : user_id
    PromoCode ..> Order : code
```

Згруповано: `User` — auth-service; `Category`, `MenuItem`, `ProductVariant`,
`ProductReview` — catalog-service; `Cart`, `CartItem`, `Order`, `OrderItem`,
`Payment`, `PromoCode` — order-service.
