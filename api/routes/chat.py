from fastapi import APIRouter, Depends
from datetime import datetime
from core.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

_messages = []

@router.post("/send")
async def send_message(data: dict, current_user: dict = Depends(get_current_user)):
    msg = {
        "from": current_user["user_id"],
        "to": data.get("to"),
        "contract_id": data.get("contract_id"),
        "message": data["message"],
        "timestamp": str(datetime.utcnow())
    }
    _messages.append(msg)
    return {"success": True, "message": msg}

@router.get("/{contract_id}")
async def get_messages(contract_id: str, current_user: dict = Depends(get_current_user)):
    return [m for m in _messages if m["contract_id"] == contract_id]