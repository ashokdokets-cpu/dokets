from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from core.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/disputes", tags=["Disputes"])

_disputes = []
_resolutions = []

@router.post("/file")
async def file_dispute(data: dict, current_user: dict = Depends(get_current_user)):
    dispute = {
        "id": f"DSP-{len(_disputes)+1:04d}",
        "contract_id": data["contract_id"],
        "filed_by": current_user["user_id"],
        "reason": data["reason"],
        "description": data.get("description", ""),
        "evidence": data.get("evidence", []),
        "status": "open",
        "filed_at": str(datetime.utcnow()),
        "resolved_at": None,
        "resolution": None
    }
    _disputes.append(dispute)
    return {"success": True, "dispute": dispute}

@router.get("/contract/{contract_id}")
async def get_disputes(contract_id: str, current_user: dict = Depends(get_current_user)):
    return [d for d in _disputes if d["contract_id"] == contract_id]

@router.put("/{dispute_id}/resolve")
async def resolve_dispute(dispute_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    for d in _disputes:
        if d["id"] == dispute_id:
            d["status"] = "resolved"
            d["resolved_at"] = str(datetime.utcnow())
            d["resolution"] = {
                "resolved_by": current_user["user_id"],
                "decision": data.get("decision", "pending"),
                "notes": data.get("notes", ""),
                "refund_percent": data.get("refund_percent", 0)
            }
            return {"success": True, "dispute": d}
    raise HTTPException(status_code=404, detail="Dispute not found")

@router.get("/stats")
async def dispute_stats():
    return {
        "total": len(_disputes),
        "open": len([d for d in _disputes if d["status"] == "open"]),
        "resolved": len([d for d in _disputes if d["status"] == "resolved"]),
        "resolution_rate": f"{len([d for d in _disputes if d['status']=='resolved'])/max(len(_disputes),1)*100:.1f}%"
    }