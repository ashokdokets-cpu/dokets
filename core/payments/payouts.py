"""
Dokets VouchAI - Instant Payout System
"""

import logging
import uuid
from datetime import datetime
from config.settings import settings

logger = logging.getLogger("dokets.payouts")

class PayoutEngine:
    def __init__(self):
        self.payouts = []
        self.methods = ["upi", "bank_transfer", "paypal", "razorpay"]
        logger.info("Payout engine ready")
    
    def request_payout(self, user_id, amount, currency="INR", method="upi", upi_id=None, bank_account=None):
        payout = {
            "id": f"PAY-{uuid.uuid4().hex[:8].upper()}",
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "method": method,
            "upi_id": upi_id,
            "bank_account": bank_account,
            "status": "processing",
            "fee": round(amount * 0.01, 2),
            "net_amount": round(amount * 0.99, 2),
            "requested_at": str(datetime.utcnow()),
            "completed_at": None,
            "instant": True
        }
        self.payouts.append(payout)
        logger.info(f"Payout created: {payout['id']} for {currency} {amount}")
        return payout
    
    def get_user_payouts(self, user_id):
        return [p for p in self.payouts if p["user_id"] == user_id]
    
    def get_payout(self, payout_id):
        for p in self.payouts:
            if p["id"] == payout_id:
                return p
        return None

payout_engine = PayoutEngine()