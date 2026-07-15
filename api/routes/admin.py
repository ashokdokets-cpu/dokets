from fastapi import APIRouter, HTTPException, Depends
from core.security.auth import get_current_user
# Using MongoDB directly now
_users = []  # Fallback
from api.routes.contracts import _contracts

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

ADMIN_EMAILS = ["contact@dokets.com"]

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