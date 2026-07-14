from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from core.security.auth import get_current_user
from api.routes.users import _users
from api.routes.contracts import _contracts
from api.routes.disputes import _disputes

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/platform")
async def platform_analytics(current_user: dict = Depends(get_current_user)):
    now = datetime.utcnow()
    
    # Monthly trends
    monthly_data = []
    for i in range(6):
        month_start = now - timedelta(days=30*(i+1))
        month_contracts = [c for c in _contracts if c.get("created_at", "") > str(month_start)]
        monthly_data.append({
            "month": month_start.strftime("%B"),
            "contracts": len(month_contracts),
            "value": sum(c.get("total_amount", 0) for c in month_contracts)
        })
    
    # Currency distribution
    currency_stats = {}
    for c in _contracts:
        curr = c.get("currency", "USD")
        currency_stats[curr] = currency_stats.get(curr, 0) + 1
    
    return {
        "users": {
            "total": len(_users),
            "providers": len([u for u in _users if u.get("user_role") == "service_provider"]),
            "customers": len([u for u in _users if u.get("user_role") == "customer"]),
            "growth": f"+{len(_users)} this month"
        },
        "contracts": {
            "total": len(_contracts),
            "active": len([c for c in _contracts if c.get("status") == "active"]),
            "completed": len([c for c in _contracts if c.get("status") == "completed"]),
            "completion_rate": f"{len([c for c in _contracts if c.get('status')=='completed'])/max(len(_contracts),1)*100:.1f}%"
        },
        "revenue": {
            "total_escrow": sum(c.get("total_amount", 0) for c in _contracts),
            "platform_fees": sum(c.get("total_amount", 0) * 0.01 for c in _contracts),
            "avg_contract": sum(c.get("total_amount", 0) for c in _contracts) / max(len(_contracts), 1)
        },
        "trends": {
            "monthly": monthly_data,
            "currencies": currency_stats,
            "top_currencies": sorted(currency_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        },
        "disputes": {
            "total": len(_disputes),
            "resolution_rate": f"{len([d for d in _disputes if d.get('status')=='resolved'])/max(len(_disputes),1)*100:.1f}%"
        }
    }

@router.get("/dashboard")
async def dashboard_analytics(current_user: dict = Depends(get_current_user)):
    uid = current_user["user_id"]
    my_contracts = [c for c in _contracts if c.get("customer_id") == uid or c.get("provider_id") == uid]
    completed = len([c for c in my_contracts if c.get("status") == "completed"])
    
    # Spending/Earning by currency
    by_currency = {}
    for c in my_contracts:
        curr = c.get("currency", "USD")
        by_currency[curr] = by_currency.get(curr, 0) + c.get("total_amount", 0)
    
    return {
        "my_stats": {
            "total": len(my_contracts),
            "completed": completed,
            "active": len([c for c in my_contracts if c.get("status") == "active"]),
            "completion_rate": f"{completed/max(len(my_contracts),1)*100:.1f}%"
        },
        "by_currency": by_currency,
        "total_value": sum(c.get("total_amount", 0) for c in my_contracts),
        "avg_value": sum(c.get("total_amount", 0) for c in my_contracts) / max(len(my_contracts), 1)
    }