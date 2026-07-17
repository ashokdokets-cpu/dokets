"""
Dokets VouchAI - Referral Program
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from core.security.auth import get_current_user
from core.database.mongodb import mongodb
import uuid

router = APIRouter(prefix="/api/v1/referrals", tags=["Referrals"])

@router.get("/code")
async def my_referral_code(current_user: dict = Depends(get_current_user)):
    """Get or create referral code"""
    db = mongodb.get_db()
    if db is not None:
        user = await db.users.find_one({"_id": current_user["user_id"]})
        code = user.get("referral_code") if user else None
        if not code:
            code = f"DOK-{uuid.uuid4().hex[:6].upper()}"
            from bson import ObjectId
            await db.users.update_one({"_id": ObjectId(current_user["user_id"])}, {"$set": {"referral_code": code}})
        return {"referral_code": code, "referral_link": f"https://dokets.com/signup?ref={code}", "earnings": user.get("referral_earnings", 0) if user else 0}
    return {"referral_code": "DOK-TEST", "referral_link": "https://dokets.com/signup?ref=DOK-TEST"}