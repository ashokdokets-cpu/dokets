"""
Dokets VouchAI - AI Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from core.security.auth import get_current_user
from core.ai.ai_engine import ai_engine

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

@router.post("/extract-contract")
async def extract_contract(data: dict, current_user: dict = Depends(get_current_user)):
    """Extract contract details from text using AI"""
    
    text = data.get("text", "")
    language = data.get("language", "en")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    result = await ai_engine.extract_contract_from_text(text, language)
    
    return {
        "success": True,
        "message": "Contract extracted successfully",
        "data": result
    }

@router.post("/verify-work")
async def verify_work(data: dict, current_user: dict = Depends(get_current_user)):
    """AI verification of work completion"""
    
    description = data.get("description", "")
    proof_text = data.get("proof_text", "")
    
    result = await ai_engine.verify_work(description, proof_text)
    
    return {
        "success": True,
        "message": "Verification complete",
        "data": result
    }

@router.post("/mediate-dispute")
async def mediate_dispute(data: dict, current_user: dict = Depends(get_current_user)):
    """AI dispute mediation"""
    
    contract = data.get("contract", {})
    dispute_text = data.get("dispute_text", "")
    
    result = await ai_engine.mediate_dispute(contract, dispute_text)
    
    return {
        "success": True,
        "message": "Mediation complete",
        "data": result
    }

@router.post("/smart-contract")
async def create_smart_contract(data: dict, current_user: dict = Depends(get_current_user)):
    """Create a complete contract from natural language description"""
    
    text = data.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text description is required")
    
    # Step 1: Extract contract details with AI
    extracted = await ai_engine.extract_contract_from_text(text)
    
    # Step 2: Create the contract with escrow (reuse contract logic)
    from api.routes.contracts import _contracts
    from core.payments.escrow import escrow_engine
    from datetime import datetime
    import uuid
    
    contract_id = f"CT-{uuid.uuid4().hex[:8].upper()}"
    
    milestones = extracted.get("milestones", [])
    escrows = []
    
    for ms in milestones:
        escrow = escrow_engine.create_escrow(
            contract_id=contract_id,
            milestone_id=ms.get("id", f"MS-{uuid.uuid4().hex[:6]}"),
            amount=ms.get("amount", 0),
            currency=extracted.get("currency", "USD"),
            customer_id=current_user["user_id"],
            provider_id=""
        )
        escrows.append(escrow)
        ms["escrow_id"] = escrow["id"]
    
    contract = {
        "id": contract_id,
        "title": extracted.get("title", "AI-Generated Contract"),
        "description": extracted.get("description", text),
        "customer_id": current_user["user_id"],
        "provider_id": None,
        "provider_phone": data.get("provider_phone", ""),
        "total_amount": extracted.get("total_amount", 0),
        "currency": extracted.get("currency", "USD"),
        "status": "draft",
        "milestones": milestones,
        "escrows": escrows,
        "ai_generated": True,
        "created_at": str(datetime.utcnow())
    }
    
    _contracts.append(contract)
    
    return {
        "success": True,
        "message": "AI-generated contract created with escrow",
        "data": {
            "contract_id": contract_id,
            "extracted_details": extracted,
            "contract": contract
        }
    }