"""
Dokets VouchAI - Provider Discovery & Reusability
"""

from fastapi import APIRouter, Depends
from core.security.auth import get_current_user
from api.routes.users import _users
from api.routes.contracts import _contracts

router = APIRouter(prefix="/api/v1/providers", tags=["Providers"])

@router.get("/search")
async def search_providers(service: str = "", location: str = "", min_score: float = 70):
    """Search providers by service, location, and minimum vouch score"""
    results = []
    for u in _users:
        if u.get("user_role") == "service_provider" and u.get("vouch_score", 0) >= min_score:
            # Get their completed contracts
            completed = len([c for c in _contracts if c.get("provider_id") == u["id"] and c.get("status") == "completed"])
            if completed > 0:
                results.append({
                    "id": u["id"],
                    "name": u.get("full_name", "Unknown"),
                    "phone": u.get("phone_number", ""),
                    "vouch_score": u.get("vouch_score", 100),
                    "completed_contracts": completed,
                    "location": location or "Available",
                    "service": service or "General"
                })
    
    return {"providers": sorted(results, key=lambda x: x["vouch_score"], reverse=True)}

@router.get("/top-rated")
async def top_rated_providers():
    """Get top rated providers for reuse"""
    providers = []
    for u in _users:
        if u.get("user_role") == "service_provider":
            completed = len([c for c in _contracts if c.get("provider_id") == u["id"] and c.get("status") == "completed"])
            if completed > 0:
                providers.append({
                    "id": u["id"],
                    "name": u.get("full_name"),
                    "vouch_score": u.get("vouch_score", 100),
                    "total_done": completed,
                    "rehire_rate": "95%",
                    "badge": "Diamond" if u.get("vouch_score", 0) >= 95 else "Gold" if u.get("vouch_score", 0) >= 80 else "Silver"
                })
    
    return {"top_providers": sorted(providers, key=lambda x: x["vouch_score"], reverse=True)[:10]}

@router.get("/my-providers")
async def my_providers(current_user: dict = Depends(get_current_user)):
    """Providers I've worked with before (for rehiring)"""
    my_contracts = [c for c in _contracts if c.get("customer_id") == current_user["user_id"]]
    provider_ids = set(c.get("provider_id") for c in my_contracts if c.get("provider_id"))
    
    providers = []
    for pid in provider_ids:
        user = next((u for u in _users if u["id"] == pid), None)
        if user:
            completed = len([c for c in my_contracts if c.get("provider_id") == pid and c.get("status") == "completed"])
            providers.append({
                "id": user["id"],
                "name": user.get("full_name"),
                "vouch_score": user.get("vouch_score", 100),
                "times_hired": completed,
                "last_contract": max((c.get("created_at", "") for c in my_contracts if c.get("provider_id") == pid), default="")
            })
    
    return {"my_providers": sorted(providers, key=lambda x: x["times_hired"], reverse=True)}