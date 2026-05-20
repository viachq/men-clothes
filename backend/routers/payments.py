import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.payment import Payment
from backend.models.order import Order
from backend.models.user import User
from backend.enums import PaymentStatus, OrderStatus
from backend.deps import get_current_user
from backend.services.liqpay import LiqPayService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create")
def create_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    existing_payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    payment = existing_payment
    if not payment:
        payment = Payment(order_id=order_id, amount=order.total_price, status=PaymentStatus.PENDING.value)
        db.add(payment)
        db.commit()
        db.refresh(payment)

    try:
        liqpay_service = LiqPayService()
        result_url = "http://localhost:5174/orders?payment=success"
        server_url = "http://localhost:8000/payments/callback"
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
    try:
        form_data = await request.form()
        data = form_data.get("data")
        signature = form_data.get("signature")
        if not data or not signature:
            raise HTTPException(status_code=400, detail="Missing data or signature")

        liqpay_service = LiqPayService()
        if not liqpay_service.verify_callback(data, signature):
            raise HTTPException(status_code=400, detail="Invalid signature")

        callback_data = liqpay_service.decode_callback_data(data)
        liqpay_order_id = callback_data.get("order_id")
        status = callback_data.get("status")
        transaction_id = callback_data.get("transaction_id")

        if "_" in str(liqpay_order_id):
            order_id_str, payment_id_str = str(liqpay_order_id).rsplit("_", 1)
            order_id = int(order_id_str)
            payment_id = int(payment_id_str)
        else:
            order_id = int(liqpay_order_id)
            payment_id = None

        if payment_id:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
        else:
            payment = db.query(Payment).filter(Payment.order_id == order_id).first()

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if status == "success":
            payment.status = PaymentStatus.COMPLETED.value
            payment.transaction_id = transaction_id
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = OrderStatus.PENDING.value
        elif status in ("failure", "error"):
            payment.status = PaymentStatus.FAILED.value

        db.commit()
        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing LiqPay callback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing callback: {str(e)}")
