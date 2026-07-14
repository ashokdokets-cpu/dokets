from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from core.security.auth import get_current_user, create_access_token
from core.payments.escrow import escrow_engine
from core.ai.vouch_score import vouch_engine
# _users is now inside users.py as _fallback_users
import uuid
from core.database.mongodb import mongodb

router = APIRouter(prefix="/api/v1/contracts", tags=["Contracts"])

_contracts = []

async def get_contracts_collection():
    db = mongodb.get_db()
    if db is not None:
        return db.contracts
    return None

@router.post("/")
async def create_contract(data: dict, current_user: dict = Depends(get_current_user)):
    # Auto-detect location & currency
    from core.ai.geo_detector import get_smart_defaults
    
    customer_phone = "+91"  # Default, will be enhanced later
    provider_phone = data.get("provider_phone", "+91")
    
    geo = get_smart_defaults(customer_phone, provider_phone)
    
    # Use auto-detected currency if not specified
    if not data.get("currency"):
        data["currency"] = geo["currency"]

    contract_id = f"CT-{uuid.uuid4().hex[:8].upper()}"
    
    milestones = data.get("milestones", [])
    escrows = []
    
    # Create escrow for each milestone
    for ms in milestones:
        escrow = escrow_engine.create_escrow(
            contract_id=contract_id,
            milestone_id=ms.get("id", f"MS-{uuid.uuid4().hex[:6]}"),
            amount=ms["amount"],
            currency=data.get("currency", "USD"),
            customer_id=current_user["user_id"],
            provider_id=""  # Will be filled when approved
        )
        escrows.append(escrow)
        ms["escrow_id"] = escrow["id"]
    
    contract = {
        "id": contract_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "customer_id": current_user["user_id"],
        "provider_id": None,
        "provider_phone": data.get("provider_phone", ""),
        "total_amount": data["total_amount"],
        "currency": data.get("currency", "USD"),
        "status": "draft",
        "milestones": milestones,
        "escrows": escrows,
        "created_at": str(datetime.utcnow()),
        "updated_at": str(datetime.utcnow())
    }

    # Save to MongoDB
    contracts_col = await get_contracts_collection()
    if contracts_col is not None:
        await contracts_col.insert_one(contract)
    _contracts.append(contract)

    # After contract is created, create a provider view link
    provider_token = create_access_token(data={"sub": "provider", "contract_id": contract_id, "email": "provider@view"})
    contract["provider_view_url"] = f"https://dokets.com/contract-view/{contract_id}?token={provider_token}"
    contract["share_url"] = f"https://dokets.com/contract-view/{contract_id}"
    
    # Send WhatsApp notification to provider
    from core.messaging.whatsapp_bot import whatsapp_bot
    whatsapp_bot.send_message(
        contract["provider_phone"],
        f"📋 *New Contract on Dokets!*\n\n"
        f"*{contract['title']}*\n"
        f"Amount: {contract['currency']} {contract['total_amount']}\n"
        f"From: {current_user['email']}\n\n"
        f"View & Approve: {contract['share_url']}\n\n"
        f"Reply 'ACCEPT {contract['id']}' to approve!"
    )
    
    return {
        "success": True,
        "message": "Contract created with escrow",
        "data": {
            "contract_id": contract_id,
            "contract": contract
        }
    }

@router.get("/")
async def get_my_contracts(current_user: dict = Depends(get_current_user)):
    contracts_col = await get_contracts_collection()
    if contracts_col is not None:
        mongo_contracts = await contracts_col.find({
            "$or": [
                {"customer_id": current_user["user_id"]},
                {"provider_id": current_user["user_id"]}
            ]
        }).to_list(length=100)
        # Merge with in-memory
        return {"contracts": mongo_contracts + _contracts, "total": len(mongo_contracts) + len(_contracts)}
    
    my_contracts = [c for c in _contracts if c["customer_id"] == current_user["user_id"] or c["provider_id"] == current_user["user_id"]]
    return {"contracts": my_contracts, "total": len(my_contracts)}

@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    for c in _contracts:
        if c["id"] == contract_id:
            return c
    raise HTTPException(status_code=404, detail="Contract not found")

@router.put("/{contract_id}/approve")
async def approve_contract(contract_id: str, current_user: dict = Depends(get_current_user)):
    for c in _contracts:
        if c["id"] == contract_id:
            c["provider_id"] = current_user["user_id"]
            c["status"] = "active"
            c["updated_at"] = str(datetime.utcnow())
            
            # Update escrows with provider ID
            for e in c.get("escrows", []):
                e["provider_id"] = current_user["user_id"]
            
            return {
                "success": True,
                "message": "Contract approved and escrow activated",
                "contract": c
            }
    raise HTTPException(status_code=404, detail="Contract not found")

@router.post("/{contract_id}/milestone/{milestone_id}/submit-proof")
async def submit_proof(contract_id: str, milestone_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Submit proof of work completion with images"""
    for c in _contracts:
        if c["id"] == contract_id:
            for ms in c.get("milestones", []):
                if ms["id"] == milestone_id:
                    ms["proof"] = {
                        "images": data.get("images", []),
                        "description": data.get("description", ""),
                        "submitted_by": current_user["user_id"],
                        "submitted_at": str(datetime.utcnow()),
                        "status": "pending_review"
                    }
                    ms["status"] = "awaiting_verification"
                    
                    # Notify provider
                    from core.messaging.whatsapp_bot import whatsapp_bot
                    whatsapp_bot.send_message(
                        c["provider_phone"],
                        f"Work Proof Submitted!\nContract: {c['title']}\nMilestone: {ms['title']}\nReview: https://dokets.com/contract-view/{contract_id}"
                    )
                    
                    return {"success": True, "message": "Proof submitted for review"}
    raise HTTPException(status_code=404, detail="Not found")

@router.put("/{contract_id}/complete-milestone/{milestone_id}")
async def complete_milestone(contract_id: str, milestone_id: str, current_user: dict = Depends(get_current_user)):
    for c in _contracts:
        if c["id"] == contract_id:
            for ms in c.get("milestones", []):
                if ms["id"] == milestone_id:
                    ms["status"] = "completed"
                    ms["completed_at"] = str(datetime.utcnow())
                    
                    # Release escrow
                    if ms.get("escrow_id"):
                        escrow_engine.release_escrow(ms["escrow_id"])
                    
                    # Check if all milestones complete
                    all_done = all(m["status"] == "completed" for m in c["milestones"])
                    if all_done:
                        c["status"] = "completed"
                        c["completed_at"] = str(datetime.utcnow())
                    
                    c["updated_at"] = str(datetime.utcnow())
                    
                    return {
                        "success": True,
                        "message": "Milestone completed and payment released",
                        "contract": c
                    }
    raise HTTPException(status_code=404, detail="Contract or milestone not found")

@router.get("/user/{user_id}/vouch-score")
async def get_vouch_score(user_id: str):
    # Calculate from contracts
    user_contracts = [
        c for c in _contracts 
        if c["provider_id"] == user_id or c["customer_id"] == user_id
    ]
    
    total = len(user_contracts)
    completed = len([c for c in user_contracts if c["status"] == "completed"])
    disputed = len([c for c in user_contracts if c["status"] == "disputed"])
    
    score = vouch_engine.calculate_score(total, completed, disputed, completed)
    level = vouch_engine.get_level(score)
    
    return {
        "user_id": user_id,
        "vouch_score": score,
        "level": level,
        "total_contracts": total,
        "completed": completed,
        "disputed": disputed
    }