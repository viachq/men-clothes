# Діаграма послідовності: реєстрація та підтвердження email

```mermaid
sequenceDiagram
    actor U as Користувач
    participant FE as Client SPA
    participant AUTH as auth-service
    participant DB as auth.db

    U->>FE: Заповнює форму реєстрації
    FE->>AUTH: POST /auth/register {username, password, email}
    AUTH->>AUTH: Валідація (довжина, складність пароля)
    AUTH->>DB: SELECT user WHERE username/email
    alt Користувач уже існує
        AUTH-->>FE: 400 "Ім'я/email вже зайняте"
        FE-->>U: Повідомлення про помилку
    else Дані вільні
        AUTH->>AUTH: bcrypt-хешування пароля
        AUTH->>AUTH: generate_verification_token() (24 год)
        AUTH->>DB: INSERT user (is_verified=false, token)
        AUTH-->>FE: 201 {message, verification_token, user}
        FE->>AUTH: GET /auth/verify-email?token=... (авто, демо-режим)
        AUTH->>DB: SELECT user WHERE verification_token
        AUTH->>AUTH: Перевірка строку дії токена
        AUTH->>DB: UPDATE is_verified=true, token=null
        AUTH-->>FE: 200 "Email підтверджено"
        FE->>AUTH: POST /auth/login {username, password}
        AUTH->>DB: SELECT user, перевірка bcrypt + is_active + is_verified
        AUTH-->>FE: 200 {access_token (JWT), user}
        FE-->>U: Вхід виконано
    end
```

У промисловому режимі крок підтвердження виконується користувачем за
посиланням з листа (SMTP). Для демонстраційного/дипломного режиму, де SMTP не
налаштовано, токен повертається у відповіді й підтвердження виконується
автоматично, зберігаючи повний серверний механізм верифікації.
