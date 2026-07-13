"""
Dokets VouchAI - Escrow Engine
"""

from datetime import datetime
from typing import Dict, List
import uuid

class EscrowEngine:
    def __init__(self):
        self.escrows = []
        self.platform_fee = 0.01  # 1%
    
    def create_escrow(self, contract_id: str, milestone_id: str, amount: float, currency: str, customer_id: str, provider_id: str) -> Dict:
        escrow = {
            "id": f"ESC-{uuid.uuid4().hex[:8].upper()}",
            "contract_id": contract_id,
            "milestone_id": milestone_id,
            "amount": amount,
            "currency": currency,
            "platform_fee": round(amount * self.platform_fee, 2),
            "provider_payout": round(amount * (1 - self.platform_fee), 2),
            "customer_id": customer_id,
            "provider_id": provider_id,
            "status": "funded",
            "created_at": str(datetime.utcnow()),
            "released_at": None
        }
        self.escrows.append(escrow)
        return escrow
    
    def release_escrow(self, escrow_id: str) -> Dict:
        for e in self.escrows:
            if e["id"] == escrow_id:
                e["status"] = "released"
                e["released_at"] = str(datetime.utcnow())
                return e
        return None
    
    def get_escrow(self, escrow_id: str) -> Dict:
        for e in self.escrows:
            if e["id"] == escrow_id:
                return e
        return None
    
    def get_contract_escrows(self, contract_id: str) -> List[Dict]:
        return [e for e in self.escrows if e["contract_id"] == contract_id]

# Global instance
escrow_engine = EscrowEngine()