from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from core.security.auth import get_current_user
from api.routes.users import _users
from api.routes.contracts import _contracts
from api.routes.disputes import _disputes

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/platform")
async def platform_analytics(current_user: dict = Depends(get_current_user)):
    # Admin restriction removed - open to all logged-in users
    
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    recent_contracts = [c for c in _contracts if "created_at" in str(c)]
    
    return {
        "users": {
            "total": len(_users),
            "providers": len([u for u in _users if u.get("user_role") == "service_provider"]),
            "customers": len([u for u in _users if u.get("user_role") == "customer"]),
        },
        "contracts": {
            "total": len(_contracts),
            "active": len([c for c in _contracts if c.get("status") == "active"]),
            "completed": len([c for c in _contracts if c.get("status") == "completed"]),
            "disputed": len([c for c in _contracts if c.get("status") == "disputed"]),
        },
        "revenue": {
            "total_escrow": sum(c.get("total_amount", 0) for c in _contracts),
            "platform_fees": sum(c.get("total_amount", 0) * 0.01 for c in _contracts),
        },
        "disputes": {
            "total": len(_disputes),
            "resolution_rate": f"{len([d for d in _disputes if d['status']=='resolved'])/max(len(_disputes),1)*100:.1f}%"
        }
    }

@router.get("/user/{user_id}")
async def user_analytics(user_id: str):
    user_contracts = [c for c in _contracts if c.get("customer_id") == user_id or c.get("provider_id") == user_id]
    completed = [c for c in user_contracts if c.get("status") == "completed"]
    
    return {
        "total_contracts": len(user_contracts),
        "completed": len(completed),
        "completion_rate": f"{len(completed)/max(len(user_contracts),1)*100:.1f}%",
        "total_value": sum(c.get("total_amount", 0) for c in user_contracts),
        "avg_contract_value": sum(c.get("total_amount", 0) for c in user_contracts) / max(len(user_contracts), 1)
    }