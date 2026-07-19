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
    """Request a payout"""
    import uuid
    from datetime import datetime
    
    payout = {
        "id": f"PAY-{uuid.uuid4().hex[:8].upper()}",
        "user_id": current_user["user_id"],
        "amount": data.get("amount", 0),
        "currency": data.get("currency", "INR"),
        "method": data.get("method", "upi"),
        "detail": data.get("upi_id") or data.get("bank_account", ""),
        "status": "pending",
        "requested_at": str(datetime.utcnow())
    }
    return {"success": True, "payout": payout}

@router.get("/payouts")
async def get_payouts(current_user: dict = Depends(get_current_user)):
    """Get my payout history"""
    payouts = await payout_engine.get_user_payouts(current_user["user_id"])
    stats = await payout_engine.get_payout_stats(current_user["user_id"])
    return {"success": True, "payouts": payouts, "stats": stats}

@router.get("/payouts/pending")
async def get_pending_payouts(current_user: dict = Depends(get_current_user)):
    """Admin: Get pending payouts"""
    payouts = await payout_engine.get_pending_payouts()
    return {"success": True, "payouts": payouts}

@router.put("/payouts/{payout_id}/approve")
async def approve_payout(payout_id: str, current_user: dict = Depends(get_current_user)):
    """Admin: Approve a payout"""
    result = await payout_engine.approve_payout(payout_id, current_user["user_id"])
    return result

@router.put("/payouts/{payout_id}/complete")
async def complete_payout(payout_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Admin: Mark payout as completed"""
    result = await payout_engine.complete_payout(payout_id, data.get("transaction_id", ""))
    return result
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

# ========== Recurring Contracts ==========
@router.post("/recurring/create")
async def create_recurring(data: dict, current_user: dict = Depends(get_current_user)):
    from core.payments.recurring import recurring
    sub = recurring.create_recurring(
        current_user["user_id"],
        data["provider_phone"],
        data["amount"],
        data.get("currency", "INR"),
        data.get("frequency", "monthly"),
        data.get("title", "Recurring Service")
    )
    return {"success": True, "subscription": sub}

@router.get("/recurring")
async def get_recurring(current_user: dict = Depends(get_current_user)):
    from core.payments.recurring import recurring
    return recurring.get_user_subscriptions(current_user["user_id"])

# ========== Invoice ==========
@router.get("/invoice/{contract_id}")
async def get_invoice(contract_id: str):
    from api.routes.contracts import _contracts
    from core.payments.invoice import generate_invoice, get_invoice_html
    
    contract = next((c for c in _contracts if c["id"] == contract_id), None)
    if not contract:
        raise HTTPException(status_code=404)
    
    invoice = generate_invoice(contract)
    return {"invoice": invoice, "html": get_invoice_html(invoice)}

# ========== Chatbot ==========
@router.post("/chatbot/ask")
async def ask_chatbot(data: dict):
    from core.ai.chatbot import chatbot
    return chatbot.get_response(data.get("question", ""))

# ========== Push Notifications ==========
@router.post("/push/subscribe")
async def subscribe_push(data: dict, current_user: dict = Depends(get_current_user)):
    from core.messaging.push_notifications import push_notifications
    return push_notifications.subscribe(current_user["user_id"], data)

@router.post("/push/send")
async def send_push(data: dict, current_user: dict = Depends(get_current_user)):
    from core.messaging.push_notifications import push_notifications
    return push_notifications.send(data["user_id"], data["title"], data["message"])

# ========== Translations ==========
@router.get("/translations/{lang}")
async def get_translations(lang: str = "en"):
    from core.ai.translations import TRANSLATIONS
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])

@router.get("/languages")
async def get_languages():
    from core.ai.translations import get_available_languages
    return get_available_languages()