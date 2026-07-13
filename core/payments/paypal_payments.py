import logging
import uuid

logger = logging.getLogger("dokets.paypal")

class PayPalPayments:
    def __init__(self):
        self.client_id = None
        logger.info("PayPal ready (test mode)")
    
    def create_order(self, amount, currency="USD"):
        order_id = f"PAYPAL-{uuid.uuid4().hex[:12]}"
        return {
            "success": True,
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "gateway": "paypal",
            "test_mode": True
        }

paypal_payments = PayPalPayments()