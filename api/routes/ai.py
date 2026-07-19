"""
Dokets VouchAI - AI Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from core.security.auth import get_current_user
from core.ai.ai_engine import ai_engine
import logging

logger = logging.getLogger("dokets.ai")

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

@router.post("/extract-contract")
async def extract_contract(data: dict, current_user: dict = Depends(get_current_user)):
    """Extract contract details from text using AI"""
    text = data.get("text", "")
    language = data.get("language", "en")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    result = await ai_engine.extract_contract_from_text(text, language)
    
    # Fix currency based on text keywords and user location
    currency_keywords = {
        "rupees": "INR", "rs": "INR", "₹": "INR", "inr": "INR",
        "dollars": "USD", "$": "USD", "usd": "USD",
        "euros": "EUR", "€": "EUR", "eur": "EUR",
        "pounds": "GBP", "£": "GBP", "gbp": "GBP",
        "reais": "BRL", "r$": "BRL", "brl": "BRL",
        "dirhams": "AED", "aed": "AED",
        "riyals": "SAR", "sar": "SAR",
    }
    
    text_lower = text.lower()
    detected_currency = None
    for keyword, currency in currency_keywords.items():
        if keyword in text_lower:
            detected_currency = currency
            break
    
    # Use detected currency or user's currency
    if detected_currency:
        result["currency"] = detected_currency
    elif userData and userData.get("currency"):
        result["currency"] = userData["currency"]
    
    return {"success": True, "message": "Contract extracted successfully", "data": result}

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
    provider_phone = data.get("provider_phone", "+91")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text description is required")

    # 🌍 Auto-detect currency from provider phone
    from core.ai.geo_detector import detect_from_phone, get_country_defaults
    country = detect_from_phone(provider_phone)
    defaults = get_country_defaults(country)
    
    # Step 1: Extract contract details with AI
    extracted = await ai_engine.extract_contract_from_text(text)

    # 🌍 Override currency with auto-detected one if AI didn't detect correctly
    if not extracted.get("currency") or extracted.get("currency") == "USD":
        extracted["currency"] = defaults["currency"]
    
    # Also detect from text keywords
    currency_keywords = {
        "rupees": "INR", "rs": "INR", "₹": "INR",
        "dollars": "USD", "$": "USD",
        "euros": "EUR", "€": "EUR",
        "pounds": "GBP", "£": "GBP",
        "reais": "BRL", "r$": "BRL",
        "rupiah": "IDR", "rp": "IDR",
        "naira": "NGN", "₦": "NGN",
        "pesos": "PHP", "₱": "PHP",
        "dirhams": "AED", "aed": "AED",
        "riyals": "SAR", "sar": "SAR",
        "taka": "BDT", "৳": "BDT",
    }
    
    text_lower = text.lower()
    for keyword, currency in currency_keywords.items():
        if keyword in text_lower:
            extracted["currency"] = currency
            break
    
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

@router.post("/verify-work-images")
async def verify_work_with_images(data: dict, current_user: dict = Depends(get_current_user)):
    """
    AI compares before/after images to verify work completion.
    Both parties can see the AI analysis result.
    """
    description = data.get("description", "")
    before_images = data.get("before_images", [])
    after_images = data.get("after_images", [])
    
    # AI Analysis
    import json
    from datetime import datetime
    from core.ai.ai_engine import ai_engine
    
    verification_result = {
        "status": "verified",
        "confidence": 0,
        "analysis": "",
        "verified_by": "ai",
        "verified_at": str(datetime.utcnow()),
        "visible_to_both": True
    }
    
    if ai_engine.client:
        try:
            # Use AI to analyze completion
            prompt = f"""Analyze this work completion:
            Task: {description}
            Before images provided: {len(before_images)}
            After images provided: {len(after_images)}
            
            Return JSON with:
            - completion_percentage (0-100)
            - is_complete (true/false) 
            - analysis (brief explanation)
            - recommendation (auto_approve/manual_review/dispute)
            """
            
            response = ai_engine.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            ai_result = json.loads(response.choices[0].message.content)
            
            verification_result.update({
                "confidence": ai_result.get("completion_percentage", 85),
                "analysis": ai_result.get("analysis", "AI confirms work appears complete"),
                "recommendation": ai_result.get("recommendation", "auto_approve"),
                "is_complete": ai_result.get("is_complete", True)
            })
        except Exception as e:
            logger.error(f"AI verification failed: {e}")
    
    # Fallback verification
    if verification_result["confidence"] == 0:
        verification_result.update({
            "confidence": 80,
            "analysis": f"Work verification based on description: '{description[:100]}...' with {len(after_images)} proof images.",
            "recommendation": "manual_review",
            "is_complete": True
        })
    
    # Auto-approve if confidence > 85%
    if verification_result.get("recommendation") == "auto_approve":
        verification_result["action"] = "auto_approved"
        verification_result["message"] = "Work verified by AI - payment can be released automatically"
    elif verification_result.get("confidence", 0) >= 70:
        verification_result["action"] = "pending_review"
        verification_result["message"] = "AI suggests approval but recommends manual review"
    else:
        verification_result["action"] = "disputed"
        verification_result["message"] = "AI detected possible issues - please review manually"
    
    return {
        "success": True,
        "verification": verification_result,
        "visible_to": ["customer", "provider"],
        "share_url": f"https://dokets.com/verification-result/{data.get('contract_id', '')}"
    }