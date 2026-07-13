from fastapi import APIRouter, HTTPException, Depends
from core.security.auth import hash_password, verify_password, create_access_token, get_current_user
from core.messaging.email_service import email_service

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

# Simple storage
_users = []

@router.post("/register")
async def register_user(data: dict):
    for u in _users:
        if u["email"] == data["email"]:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    user = {
        "id": str(len(_users) + 1),
        "email": data["email"],
        "phone_number": data["phone_number"],
        "full_name": data["full_name"],
        "hashed_password": hash_password(data["password"]),
        "user_role": data.get("user_role", "customer"),
        "vouch_score": 100.0,
        "total_contracts": 0
    }
    
    _users.append(user)
    
    return {"success": True, "message": "User registered", "data": {"user_id": user["id"]}}

@router.post("/login")
async def login_user(data: dict):
    user = None
    for u in _users:
        if u["email"] == data["email"]:
            user = u
            break
    
    if not user or not verify_password(data["password"], user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token(data={"sub": user["id"], "email": user["email"]})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "phone_number": user["phone_number"],
            "full_name": user["full_name"],
            "user_role": user["user_role"],
            "vouch_score": user["vouch_score"],
            "total_contracts": user["total_contracts"]
        }
    }

@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    user = None
    for u in _users:
        if u["id"] == current_user["user_id"]:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "phone_number": user["phone_number"],
        "full_name": user["full_name"],
        "user_role": user["user_role"],
        "vouch_score": user["vouch_score"],
        "total_contracts": user["total_contracts"]
    }

@router.post("/send-verification")
async def send_verification(data: dict, current_user: dict = Depends(get_current_user)):
    token = email_service.send_verification(data.get("email", current_user["email"]))
    return {"success": True, "message": "Verification email sent", "token": token}

@router.post("/verify-email")
async def verify_email(data: dict):
    verified = email_service.verify_email(data["email"], data["token"])
    return {"success": verified, "message": "Email verified" if verified else "Invalid token"}