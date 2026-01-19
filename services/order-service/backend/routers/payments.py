"""
Payment endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import logging

from backend.database import get_db
from backend.models.payment import Payment
from backend.models.order import Order
from backend.core.enums import PaymentStatus, OrderStatus
from backend.deps import get_current_user
from backend.models.user import User
from backend.services.liqpay_service import LiqPayService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create")
def create_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create LiqPay payment data for an order."""
    # Перевіряємо що замовлення існує і належить користувачу
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Перевіряємо чи є вже payment для цього замовлення
    existing_payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    
    if existing_payment:
        payment = existing_payment
    else:
        # Створюємо новий payment
        payment = Payment(
            order_id=order_id,
            amount=order.total_price,
            status=PaymentStatus.PENDING.value
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
    
    # Створюємо LiqPay дані
    try:
        liqpay_service = LiqPayService()
        
        # Формуємо URL для повернення
        result_url = f"http://localhost:5174/orders?payment=success"
        server_url = f"http://localhost:8003/payments/callback"
        
        # Використовуємо payment.id як order_id для LiqPay, щоб забезпечити унікальність
        # Це дозволяє створювати кілька платежів для одного замовлення
        liqpay_order_id = f"{order_id}_{payment.id}"
        
        payment_data = liqpay_service.create_payment_data(
            order_id=liqpay_order_id,
            amount=order.total_price,
            currency="UAH",
            description=f"Оплата замовлення #{order_id}",
            result_url=result_url,
            server_url=server_url,
        )
        
        return {
            "payment_id": payment.id,
            "order_id": order_id,
            "amount": order.total_price,
            "status": payment.status,
            "liqpay_data": payment_data["data"],
            "liqpay_signature": payment_data["signature"],
        }
    except Exception as e:
        logger.error(f"Error creating LiqPay payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")


@router.post("/callback")
async def liqpay_callback(request: Request, db: Session = Depends(get_db)):
    """Handle LiqPay callback."""
    try:
        form_data = await request.form()
        data = form_data.get("data")
        signature = form_data.get("signature")
        
        if not data or not signature:
            logger.error("Missing data or signature in LiqPay callback")
            raise HTTPException(status_code=400, detail="Missing data or signature")
        
        # Перевіряємо підпис
        liqpay_service = LiqPayService()
        if not liqpay_service.verify_callback(data, signature):
            logger.error("Invalid signature in LiqPay callback")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Декодуємо дані
        callback_data = liqpay_service.decode_callback_data(data)
        liqpay_order_id = callback_data.get("order_id")
        status = callback_data.get("status")
        transaction_id = callback_data.get("transaction_id")
        
        # order_id в LiqPay має формат "order_id_payment_id"
        # Витягуємо order_id та payment_id
        if "_" in str(liqpay_order_id):
            order_id_str, payment_id_str = str(liqpay_order_id).rsplit("_", 1)
            order_id = int(order_id_str)
            payment_id = int(payment_id_str)
        else:
            # Fallback для старих платежів
            order_id = int(liqpay_order_id)
            payment_id = None
        
        logger.info(f"LiqPay callback for order {order_id}, payment {payment_id}: status={status}")
        
        # Оновлюємо payment
        if payment_id:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
        else:
            # Fallback для старих платежів
            payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        
        if not payment:
            logger.error(f"Payment not found for order {order_id}, payment_id {payment_id}")
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Оновлюємо статус payment
        if status == "success":
            payment.status = PaymentStatus.COMPLETED.value
            payment.transaction_id = transaction_id
            
            # Оновлюємо статус замовлення
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = OrderStatus.PENDING.value  # Після оплати замовлення стає pending
        elif status == "failure" or status == "error":
            payment.status = PaymentStatus.FAILED.value
        
        db.commit()
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing LiqPay callback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing callback: {str(e)}")


