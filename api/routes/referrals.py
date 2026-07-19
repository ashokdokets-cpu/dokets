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

@router.post("/track")
async def track_referral(data: dict):
    """Track a referral signup"""
    ref_code = data.get("referral_code", "")
    new_user = data.get("new_user", "")
    
    db = mongodb.get_db()
    if db is not None:
        # Find the referrer
        referrer = await db.users.find_one({"referral_code": ref_code})
        if referrer:
            # Add referral earnings (e.g., Rs 50 per signup)
            current_earnings = referrer.get("referral_earnings", 0)
            from bson import ObjectId
            await db.users.update_one(
                {"_id": referrer["_id"]},
                {"$set": {"referral_earnings": current_earnings + 50}}
            )
            return {"success": True, "message": "Referral tracked!"}
    
    return {"success": False, "message": "Invalid referral code"}