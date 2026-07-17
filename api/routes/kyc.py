"""
Dokets VouchAI - Global KYC Verification
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from core.security.auth import get_current_user
from core.database.mongodb import mongodb

router = APIRouter(prefix="/api/v1/kyc", tags=["KYC"])

ID_TYPES = {
    "IN": ["aadhaar", "pan", "voter_id", "passport", "driving_license"],
    "US": ["ssn", "passport", "driving_license", "state_id"],
    "GB": ["passport", "driving_license", "national_insurance"],
    "BR": ["cpf", "rg", "passport", "cnh"],
    "ID": ["ktp", "npwp", "passport", "sim"],
    "NG": ["nin", "voter_card", "passport", "drivers_license"],
    "PH": ["umid", "passport", "drivers_license", "sss"],
    "AE": ["emirates_id", "passport"],
    "SA": ["national_id", "passport", "iqama"],
    "DE": ["passport", "personalausweis", "aufenthaltstitel"],
    "FR": ["passport", "carte_identite", "titre_sejour"],
    "ES": ["dni", "nie", "passport"],
    "OTHER": ["passport", "national_id", "driving_license"]
}

@router.get("/id-types/{country_code}")
async def get_id_types(country_code: str = "IN"):
    return {"country": country_code, "id_types": ID_TYPES.get(country_code, ID_TYPES["OTHER"])}

@router.post("/submit")
async def submit_kyc(data: dict, current_user: dict = Depends(get_current_user)):
    db = mongodb.get_db()
    kyc = {
        "user_id": current_user["user_id"],
        "name": data.get("name"),
        "id_type": data.get("id_type", "passport"),
        "id_number": data.get("id_number"),
        "country": data.get("country", "IN"),
        "document_url": data.get("document_url", ""),
        "status": "pending",
        "verified": False,
        "submitted_at": str(datetime.utcnow()),
        "verified_at": None
    }
    if db is not None:
        await db.kyc.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": kyc},
            upsert=True
        )
    return {"success": True, "message": "KYC submitted", "kyc": kyc}

@router.get("/status")
async def kyc_status(current_user: dict = Depends(get_current_user)):
    db = mongodb.get_db()
    if db is not None:
        kyc = await db.kyc.find_one({"user_id": current_user["user_id"]})
        if kyc:
            kyc["_id"] = str(kyc["_id"])
            return {"verified": kyc.get("verified", False), "status": kyc.get("status", "not_submitted"), "kyc": kyc}
    return {"verified": False, "status": "not_submitted"}