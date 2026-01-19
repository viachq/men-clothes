"""
LiqPay payment service integration.
"""
import base64
import json
import hashlib
import logging
from typing import Dict, Any, Optional
from decimal import Decimal

from backend.core.config import (
    LIQPAY_PUBLIC_KEY,
    LIQPAY_PRIVATE_KEY,
    LIQPAY_SANDBOX_MODE,
)

logger = logging.getLogger(__name__)

# Для SHA3-256
HAS_CRYPTO = None
try:
    # Спочатку пробуємо pycryptodome
    from Crypto.Hash import SHA3_256
    HAS_CRYPTO = True
except ImportError:
    try:
        # Python 3.6+ має hashlib.sha3_256
        if hasattr(hashlib, 'sha3_256'):
            HAS_CRYPTO = False
        else:
            HAS_CRYPTO = None
    except Exception:
        HAS_CRYPTO = None


class LiqPayService:
    def __init__(self) -> None:
        if not LIQPAY_PUBLIC_KEY or not LIQPAY_PRIVATE_KEY:
            raise RuntimeError("LiqPay keys are not configured")
        self.public_key = LIQPAY_PUBLIC_KEY
        self.private_key = LIQPAY_PRIVATE_KEY
        self.sandbox_mode = LIQPAY_SANDBOX_MODE

    @staticmethod
    def _to_liqpay_amount(amount: int) -> float:
        """Конвертує суму з копійок в гривні для LiqPay"""
        return float(amount) / 100.0

    def _make_signature(self, data: str, use_sha3: bool = False) -> str:
        """Створює підпис для LiqPay
        
        Для форми оплати (checkout) використовується SHA1
        Для callback використовується SHA3-256
        """
        signature_string = self.private_key + data + self.private_key
        
        if use_sha3:
            # Використовуємо SHA3-256 для callback (згідно з документацією)
            if HAS_CRYPTO is True:
                # Якщо є pycryptodome
                sha3 = SHA3_256.new()
                sha3.update(signature_string.encode('utf-8'))
                return base64.b64encode(sha3.digest()).decode('utf-8')
            elif HAS_CRYPTO is False:
                # Використовуємо hashlib.sha3_256 (Python 3.6+)
                sha3 = hashlib.sha3_256()
                sha3.update(signature_string.encode('utf-8'))
                return base64.b64encode(sha3.digest()).decode('utf-8')
            else:
                # Fallback на SHA1 якщо SHA3-256 недоступний
                logger.warning("SHA3-256 not available, using SHA1 for callback (may not work correctly)")
                return base64.b64encode(hashlib.sha1(signature_string.encode('utf-8')).digest()).decode('utf-8')
        else:
            # Використовуємо SHA1 для форми оплати (стандартний спосіб)
            return base64.b64encode(hashlib.sha1(signature_string.encode('utf-8')).digest()).decode('utf-8')

    def create_payment_data(
        self,
        order_id: str | int,  # може бути рядок або число
        amount: int,  # в копійках
        currency: str = "UAH",
        description: str = "",
        result_url: str = "",
        server_url: str = "",
    ) -> Dict[str, Any]:
        """Створює дані для форми оплати LiqPay"""
        amount_float = self._to_liqpay_amount(amount)
        
        params = {
            "version": "3",
            "public_key": self.public_key,
            "action": "pay",
            "amount": amount_float,
            "currency": currency.upper(),
            "description": description or f"Оплата замовлення #{order_id}",
            "order_id": str(order_id),
        }
        
        # Додаємо URL тільки якщо вони вказані
        if result_url:
            params["result_url"] = result_url
        if server_url:
            params["server_url"] = server_url

        # Enable sandbox mode
        if self.sandbox_mode or self.public_key.startswith("sandbox_"):
            params["sandbox"] = 1

        # Кодуємо дані в base64
        data = base64.b64encode(json.dumps(params, separators=(',', ':')).encode('utf-8')).decode('utf-8')
        
        # Створюємо підпис
        signature = self._make_signature(data)

        return {
            "data": data,
            "signature": signature,
        }

    def verify_callback(self, data: str, signature: str) -> bool:
        """Перевіряє підпис від LiqPay callback (використовує SHA3-256)"""
        expected_signature = self._make_signature(data, use_sha3=True)
        return signature == expected_signature

    def decode_callback_data(self, data: str) -> Dict[str, Any]:
        """Декодує дані з LiqPay callback"""
        decoded = base64.b64decode(data).decode('utf-8')
        return json.loads(decoded)

    def check_payment_status(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Перевіряє статус платежу через API LiqPay (action: status)"""
        try:
            import urllib.request
            import urllib.parse
            
            # Використовуємо version 3 для сумісності
            params = {
                "version": "3",
                "public_key": self.public_key,
                "action": "status",
                "order_id": str(order_id),
            }
            
            # Кодуємо дані в base64
            data = base64.b64encode(json.dumps(params, separators=(',', ':')).encode('utf-8')).decode('utf-8')
            
            # Створюємо підпис
            signature = self._make_signature(data)
            
            logger.info(f"Checking LiqPay status for order {order_id}")
            
            # Відправляємо запит до LiqPay API
            post_data = urllib.parse.urlencode({
                "data": data,
                "signature": signature,
            }).encode('utf-8')
            
            req = urllib.request.Request(
                "https://www.liqpay.ua/api/request",
                data=post_data,
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                response_text = response.read().decode('utf-8')
                logger.info(f"LiqPay API response for order {order_id}: {response_text[:500]}")
                result_data = json.loads(response_text)
                
                # LiqPay повертає {"result": "ok", "status": "success", ...} або {"result": "error", ...}
                if result_data.get("result") == "ok":
                    logger.info(f"LiqPay status data for order {order_id}: status={result_data.get('status')}, order_id={result_data.get('order_id')}")
                    return result_data
                elif result_data.get("result") == "error":
                    error_message = result_data.get("err_description", result_data.get("message", "Unknown error"))
                    logger.warning(f"LiqPay API error for order {order_id}: {error_message}")
                    return None
                else:
                    logger.warning(f"LiqPay API unknown response format for order {order_id}: {result_data}")
                    return None
            
        except Exception as e:
            logger.error(f"Error checking LiqPay status for order {order_id}: {str(e)}", exc_info=True)
            return None
