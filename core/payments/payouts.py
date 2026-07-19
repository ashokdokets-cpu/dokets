"""
Dokets VouchAI - Global Payout Engine
"""
import uuid
from datetime import datetime
from core.database.mongodb import mongodb
import logging

logger = logging.getLogger("dokets.payouts")

class PayoutValidator:
    """Global payout detail validator"""
    
    @staticmethod
    def validate_upi(upi_id: str) -> bool:
        """Validate Indian UPI ID format"""
        import re
        return bool(re.match(r'^[\w.-]+@[\w]+$', upi_id))
    
    @staticmethod
    def validate_iban(iban: str) -> bool:
        """Validate IBAN (Europe, Middle East, etc.)"""
        import re
        return bool(re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$', iban.replace(' ', '')))
    
    @staticmethod
    def validate_us_account(routing: str, account: str) -> bool:
        """Validate US bank details"""
        import re
        return bool(re.match(r'^\d{9}$', routing)) and bool(re.match(r'^\d{8,17}$', account))
    
    @staticmethod
    def validate_uk_account(sort_code: str, account: str) -> bool:
        """Validate UK bank details"""
        import re
        return bool(re.match(r'^\d{6}$', sort_code)) and bool(re.match(r'^\d{8}$', account))
    
    @staticmethod
    def validate_global(detail: str, method: str, currency: str) -> dict:
        """Validate payout details based on method and currency"""
        import re
        
        result = {"valid": True, "message": "", "normalized": detail}
        
        if method == "upi":
            if not PayoutValidator.validate_upi(detail):
                result = {"valid": False, "message": "Invalid UPI ID format (e.g., name@upi)"}
        
        elif method == "bank":
            # Detect format by currency/country patterns
            cleaned = detail.replace(' ', '').replace('-', '')
            
            if currency == "INR":
                # Indian: IFSC + Account (e.g., SBIN0001234|12345678901)
                parts = detail.split('|')
                if len(parts) == 2:
                    ifsc, acct = parts[0].strip(), parts[1].strip()
                    if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc):
                        result = {"valid": False, "message": "Invalid IFSC code"}
                    elif not re.match(r'^\d{9,18}$', acct):
                        result = {"valid": False, "message": "Invalid account number"}
                    else:
                        result["normalized"] = f"{ifsc}|{acct}"
                else:
                    result = {"valid": False, "message": "Format: IFSC|Account (e.g., SBIN0001234|12345678901)"}
            
            elif currency in ["USD", "CAD"]:
                parts = detail.split('|')
                if len(parts) == 2:
                    routing, acct = parts[0].strip(), parts[1].strip()
                    if not PayoutValidator.validate_us_account(routing, acct):
                        result = {"valid": False, "message": "Invalid routing (9 digits) or account (8-17 digits)"}
                    else:
                        result["normalized"] = f"{routing}|{acct}"
                else:
                    result = {"valid": False, "message": "Format: Routing|Account (e.g., 123456789|12345678901)"}
            
            elif currency in ["EUR", "GBP", "AED", "SAR"]:
                # IBAN format
                if not PayoutValidator.validate_iban(cleaned):
                    result = {"valid": False, "message": "Invalid IBAN format"}
                else:
                    result["normalized"] = cleaned
            
            elif currency in ["GBP"]:
                parts = detail.split('|')
                if len(parts) == 2:
                    sort, acct = parts[0].strip(), parts[1].strip()
                    if not PayoutValidator.validate_uk_account(sort, acct):
                        result = {"valid": False, "message": "Invalid sort code (6 digits) or account (8 digits)"}
                    else:
                        result["normalized"] = f"{sort}|{acct}"
                else:
                    result = {"valid": False, "message": "Format: SortCode|Account (e.g., 123456|12345678)"}
        
        return result

class PayoutEngine:
    def __init__(self):
        self.platform_fee = 0.01  # 1%

    async def request_payout(self, user_id: str, amount: float, currency: str = "INR", method: str = "upi", detail: str = ""):
        """Request a payout - saved to MongoDB"""
        # Validate payout details
        validator = PayoutValidator()
        validation = validator.validate_global(detail, method, currency)
        if not validation["valid"]:
            return {"success": False, "error": validation["message"]}
        detail = validation["normalized"]
        
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
