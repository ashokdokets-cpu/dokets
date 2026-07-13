from fastapi import APIRouter, Depends
from core.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/kyc", tags=["KYC"])

_kyc_data = {}

@router.post("/submit")
async def submit_kyc(data: dict, current_user: dict = Depends(get_current_user)):
    _kyc_data[current_user["user_id"]] = {
        "name": data.get("name"),
        "id_type": data.get("id_type", "aadhaar"),
        "id_number": data.get("id_number"),
        "status": "pending",
        "verified": False
    }
    return {"success": True, "message": "KYC submitted for verification"}

@router.get("/status")
async def kyc_status(current_user: dict = Depends(get_current_user)):
    kyc = _kyc_data.get(current_user["user_id"])
    return {"verified": kyc["verified"] if kyc else False, "status": kyc["status"] if kyc else "not_submitted"}