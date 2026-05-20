import base64
import json
import hashlib
import logging
from typing import Dict, Any, Optional

from backend.config import LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY, LIQPAY_SANDBOX_MODE

logger = logging.getLogger(__name__)

HAS_CRYPTO = None
try:
    from Crypto.Hash import SHA3_256
    HAS_CRYPTO = True
except ImportError:
    if hasattr(hashlib, "sha3_256"):
        HAS_CRYPTO = False


class LiqPayService:
    def __init__(self) -> None:
        if not LIQPAY_PUBLIC_KEY or not LIQPAY_PRIVATE_KEY:
            raise RuntimeError("LiqPay keys are not configured")
        self.public_key = LIQPAY_PUBLIC_KEY
        self.private_key = LIQPAY_PRIVATE_KEY
        self.sandbox_mode = LIQPAY_SANDBOX_MODE

    @staticmethod
    def _to_liqpay_amount(amount: int) -> float:
        return float(amount) / 100.0

    def _make_signature(self, data: str, use_sha3: bool = False) -> str:
        sig_str = self.private_key + data + self.private_key
        if use_sha3:
            if HAS_CRYPTO is True:
                sha3 = SHA3_256.new()
                sha3.update(sig_str.encode("utf-8"))
                return base64.b64encode(sha3.digest()).decode("utf-8")
            elif HAS_CRYPTO is False:
                sha3 = hashlib.sha3_256()
                sha3.update(sig_str.encode("utf-8"))
                return base64.b64encode(sha3.digest()).decode("utf-8")
            else:
                return base64.b64encode(hashlib.sha1(sig_str.encode("utf-8")).digest()).decode("utf-8")
        return base64.b64encode(hashlib.sha1(sig_str.encode("utf-8")).digest()).decode("utf-8")

    def create_payment_data(
        self, order_id: str | int, amount: int, currency: str = "UAH",
        description: str = "", result_url: str = "", server_url: str = "",
    ) -> Dict[str, Any]:
        params: dict[str, Any] = {
            "version": "3",
            "public_key": self.public_key,
            "action": "pay",
            "amount": self._to_liqpay_amount(amount),
            "currency": currency.upper(),
            "description": description or f"Оплата замовлення #{order_id}",
            "order_id": str(order_id),
        }
        if result_url:
            params["result_url"] = result_url
        if server_url:
            params["server_url"] = server_url
        if self.sandbox_mode or self.public_key.startswith("sandbox_"):
            params["sandbox"] = 1

        data = base64.b64encode(json.dumps(params, separators=(",", ":")).encode("utf-8")).decode("utf-8")
        signature = self._make_signature(data)
        return {"data": data, "signature": signature}

    def verify_callback(self, data: str, signature: str) -> bool:
        return signature == self._make_signature(data, use_sha3=True)

    def decode_callback_data(self, data: str) -> Dict[str, Any]:
        return json.loads(base64.b64decode(data).decode("utf-8"))
