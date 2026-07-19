"""
Dokets VouchAI - Global Payout Engine
"""
import uuid
from datetime import datetime
from core.database.mongodb import mongodb
import logging

logger = logging.getLogger("dokets.payouts")

class PayoutEngine:
    def __init__(self):
        self.platform_fee = 0.01  # 1%

    async def request_payout(self, user_id: str, amount: float, currency: str = "INR", method: str = "upi", detail: str = ""):
        """Request a payout - saved to MongoDB"""
        db = mongodb.get_db()
        
        payout = {
            "id": f"PAY-{uuid.uuid4().hex[:8].upper()}",
            "user_id": user_id,
            "amount": amount,
            "fee": round(amount * self.platform_fee, 2),
            "net_amount": round(amount * (1 - self.platform_fee), 2),
            "currency": currency,
            "method": method,
            "detail": detail,  # UPI ID or Bank Account
            "status": "pending",  # pending -> approved -> completed
            "requested_at": str(datetime.utcnow()),
            "approved_at": None,
            "completed_at": None,
            "approved_by": None
        }
        
        if db is not None:
            await db.payouts.insert_one(payout)
        
        logger.info(f"Payout requested: {payout['id']} - {currency} {amount}")
        return payout

    async def get_user_payouts(self, user_id: str):
        """Get all payouts for a user"""
        db = mongodb.get_db()
        if db is not None:
            payouts = await db.payouts.find({"user_id": user_id}).sort("requested_at", -1).to_list(length=50)
            for p in payouts:
                p["_id"] = str(p["_id"])
            return payouts
        return []

    async def get_pending_payouts(self):
        """Get all pending payouts (for admin)"""
        db = mongodb.get_db()
        if db is not None:
            payouts = await db.payouts.find({"status": "pending"}).sort("requested_at", 1).to_list(length=50)
            for p in payouts:
                p["_id"] = str(p["_id"])
            return payouts
        return []

    async def approve_payout(self, payout_id: str, admin_id: str):
        """Admin approves a payout"""
        db = mongodb.get_db()
        if db is not None:
            await db.payouts.update_one(
                {"id": payout_id},
                {"$set": {
                    "status": "approved",
                    "approved_at": str(datetime.utcnow()),
                    "approved_by": admin_id
                }}
            )
            logger.info(f"Payout approved: {payout_id}")
            return {"success": True, "message": "Payout approved"}
        return {"success": False, "message": "Database error"}

    async def complete_payout(self, payout_id: str, transaction_id: str = ""):
        """Mark payout as completed (after actual transfer)"""
        db = mongodb.get_db()
        if db is not None:
            await db.payouts.update_one(
                {"id": payout_id},
                {"$set": {
                    "status": "completed",
                    "completed_at": str(datetime.utcnow()),
                    "transaction_id": transaction_id
                }}
            )
            logger.info(f"Payout completed: {payout_id}")
            return {"success": True, "message": "Payout completed"}
        return {"success": False, "message": "Database error"}

    async def get_payout_stats(self, user_id: str):
        """Get payout statistics for a user"""
        payouts = await self.get_user_payouts(user_id)
        total_requested = sum(p["amount"] for p in payouts)
        total_paid = sum(p["amount"] for p in payouts if p["status"] == "completed")
        pending = sum(p["amount"] for p in payouts if p["status"] == "pending")
        return {
            "total_requested": total_requested,
            "total_paid": total_paid,
            "pending": pending,
            "total_payouts": len(payouts)
        }

payout_engine = PayoutEngine()
