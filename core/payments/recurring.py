"""
Dokets VouchAI - Recurring Contracts
"""

import uuid
from datetime import datetime

class RecurringContracts:
    def __init__(self):
        self.subscriptions = []
    
    def create_recurring(self, user_id, provider_phone, amount, currency, frequency="monthly", title="Recurring Service"):
        sub = {
            "id": f"SUB-{uuid.uuid4().hex[:8].upper()}",
            "user_id": user_id,
            "provider_phone": provider_phone,
            "amount": amount,
            "currency": currency,
            "frequency": frequency,  # weekly, monthly, quarterly
            "title": title,
            "status": "active",
            "created_at": str(datetime.utcnow()),
            "next_payment": str(datetime.utcnow()),
            "total_payments": 0
        }
        self.subscriptions.append(sub)
        return sub
    
    def get_user_subscriptions(self, user_id):
        return [s for s in self.subscriptions if s["user_id"] == user_id]
    
    def cancel_subscription(self, sub_id):
        for s in self.subscriptions:
            if s["id"] == sub_id:
                s["status"] = "cancelled"
                return s
        return None

recurring = RecurringContracts()