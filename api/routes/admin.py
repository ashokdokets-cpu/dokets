from fastapi import APIRouter, HTTPException, Depends
from core.security.auth import get_current_user
from core.database.mongodb import mongodb
_users = []  # Will use in-memory fallback
from api.routes.contracts import _contracts

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

ADMIN_EMAILS = ["contact@dokets.com", "test@dokets.com", "admin@dokets.com"]

def check_admin(current_user: dict):
    if current_user.get("email") not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail=f"Admin access required. Your email: {current_user.get('email')}")
    return current_user

@router.get("/stats")
async def admin_stats(current_user: dict = Depends(get_current_user)):
    check_admin(current_user)
    
    return {
        "total_users": len(_users),
        "total_contracts": len(_contracts),
        "active_contracts": len([c for c in _contracts if c.get("status") == "active"]),
        "completed_contracts": len([c for c in _contracts if c.get("status") == "completed"]),
        "escrow_total": sum(c.get("total_amount", 0) for c in _contracts),
        "users": [{"email": u["email"], "role": u.get("user_role"), "vouch_score": u.get("vouch_score")} for u in _users],
        "contracts": [{"id": c["id"], "title": c["title"], "status": c.get("status"), "amount": c.get("total_amount")} for c in _contracts]
    }

@router.delete("/contracts/clean")
async def clean_contracts(current_user: dict = Depends(get_current_user)):
    """Admin: Delete all contracts"""
    if current_user.get("email") not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from api.routes.contracts import _contracts
    count = len(_contracts)
    _contracts.clear()
    
    # Also clear from MongoDB
    db = mongodb.get_db()
    if db is not None:
        try:
            await db.contracts.delete_many({})
        except:
            pass
    
    return {"success": True, "message": f"Deleted {count} contracts"}