# Діаграма станів: життєвий цикл замовлення

```mermaid
stateDiagram-v2
    [*] --> pending : Створення замовлення
    pending --> delivering : Менеджер підтверджує / оплата успішна
    pending --> cancelled : Клієнт скасовує (тільки зі стану pending)
    delivering --> delivered : Доставлено
    delivered --> [*]
    cancelled --> [*]

    note right of pending
        Оплата: pending → completed (LiqPay callback)
        Скасування доступне лише власнику
        і лише поки замовлення в стані pending
    end note
```

Статуси оплати (Payment.status): `pending` → `completed` | `failed` |
`refunded`. Статус оплати оновлюється асинхронно через webhook LiqPay
(`POST /payments/callback`).
