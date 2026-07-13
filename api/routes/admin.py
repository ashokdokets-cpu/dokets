from fastapi import APIRouter, HTTPException, Depends
from core.security.auth import get_current_user
from api.routes.users import _users
from api.routes.contracts import _contracts

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

ADMIN_EMAILS = ["admin@dokets.com"]

@router.get("/stats")
async def admin_stats(current_user: dict = Depends(get_current_user)):
    if current_user["email"] not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {
        "total_users": len(_users),
        "total_contracts": len(_contracts),
        "active_contracts": len([c for c in _contracts if c["status"] == "active"]),
        "escrow_total": sum(c.get("total_amount", 0) for c in _contracts),
        "users": [{"email": u["email"], "vouch_score": u.get("vouch_score", 0)} for u in _users],
        "contracts": [{"id": c["id"], "title": c["title"], "status": c["status"]} for c in _contracts]
    }

@router.get("/users")
async def list_users(current_user: dict = Depends(get_current_user)):
    if current_user["email"] not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"users": _users}

@router.get("/contracts")
async def list_all_contracts(current_user: dict = Depends(get_current_user)):
    if current_user["email"] not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"contracts": _contracts}