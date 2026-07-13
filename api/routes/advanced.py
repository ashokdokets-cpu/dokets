from fastapi import APIRouter, Depends
from core.security.auth import get_current_user
from core.payments.payouts import payout_engine
from core.messaging.video_calls import video_engine
from core.security.background_check import background_checks
from core.payments.whitelabel import whitelabel
from core.messaging.support import support

router = APIRouter(prefix="/api/v1", tags=["Advanced"])

# ========== Payouts ==========
@router.post("/payouts/request")
async def request_payout(data: dict, current_user: dict = Depends(get_current_user)):
    payout = payout_engine.request_payout(
        current_user["user_id"],
        data["amount"],
        data.get("currency", "INR"),
        data.get("method", "upi"),
        data.get("upi_id"),
        data.get("bank_account")
    )
    return {"success": True, "payout": payout}

@router.get("/payouts")
async def get_payouts(current_user: dict = Depends(get_current_user)):
    return payout_engine.get_user_payouts(current_user["user_id"])

# ========== Video Calls ==========
@router.post("/video/create")
async def create_meeting(data: dict, current_user: dict = Depends(get_current_user)):
    meeting = video_engine.create_meeting(
        data["contract_id"],
        current_user["user_id"],
        data.get("guest_id", ""),
        data.get("topic", "Contract Discussion")
    )
    return {"success": True, "meeting": meeting, "join_url": meeting["jitsi_url"]}

@router.get("/video/{meeting_id}/join")
async def join_meeting(meeting_id: str, current_user: dict = Depends(get_current_user)):
    result = video_engine.join_meeting(meeting_id)
    return result if result else {"success": False}

# ========== Background Check ==========
@router.post("/background/request")
async def request_background_check(data: dict, current_user: dict = Depends(get_current_user)):
    check = background_checks.request_check(current_user["user_id"], data.get("provider", "manual"))
    return {"success": True, "check": check}

@router.get("/background/status")
async def background_status(current_user: dict = Depends(get_current_user)):
    return background_checks.get_user_checks(current_user["user_id"])

# ========== White Label ==========
@router.post("/agency/create")
async def create_agency(data: dict, current_user: dict = Depends(get_current_user)):
    agency = whitelabel.create_agency(current_user["user_id"], data["name"], data["domain"], data)
    return {"success": True, "agency": agency}

@router.get("/agency/{agency_id}")
async def get_agency(agency_id: str):
    return whitelabel.get_agency(agency_id)

# ========== Support ==========
@router.get("/support/faqs")
async def get_faqs():
    return support.get_faqs()

@router.post("/support/tickets")
async def create_ticket(data: dict, current_user: dict = Depends(get_current_user)):
    ticket = support.create_ticket(current_user["user_id"], data["subject"], data["message"])
    return {"success": True, "ticket": ticket}