from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from core.security.auth import get_current_user
from core.payments.escrow import escrow_engine
from core.ai.vouch_score import vouch_engine
import uuid

router = APIRouter(prefix="/api/v1/contracts", tags=["Contracts"])

_contracts = []

@router.post("/")
async def create_contract(data: dict, current_user: dict = Depends(get_current_user)):
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
    
    _contracts.append(contract)
    
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
    my_contracts = [
        c for c in _contracts 
        if c["customer_id"] == current_user["user_id"] or c["provider_id"] == current_user["user_id"]
    ]
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