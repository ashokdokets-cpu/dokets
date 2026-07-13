from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

_webhook_subscribers = []

@router.post("/register")
async def register_webhook(data: dict):
    _webhook_subscribers.append({
        "url": data["url"],
        "events": data.get("events", ["contract.created", "contract.completed"]),
        "secret": data.get("secret")
    })
    return {"success": True}

# Events would trigger POST to subscriber URLs