from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timedelta
from core.security.auth import (
    hash_password, verify_password, create_login_token, 
    create_switch_token, get_current_user
)
from core.database.mongodb import mongodb
from core.security.limiter import limiter
from core.security.validator import security as validator

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

async def get_users_collection():
    db = mongodb.get_db()
    if db is not None:
        return db.users
    return None

@router.post("/register")
@limiter.limit("5/minute")
async def register_user(request: Request, data: dict):
    """Register a new user. Mode selected at login, not registration."""
    # Validate password strength
    valid, msg = validator.validate_password_strength(data.get("password", ""))
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    email_valid, email = validator.validate_email(data.get("email", ""))
    if not email_valid:
        raise HTTPException(status_code=400, detail="Invalid email")

    phone_valid, phone = validator.validate_phone(data.get("phone_number", ""))
    if not phone_valid:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    full_name = validator.sanitize_string(data.get("full_name", "User"))

    users = await get_users_collection()
    if users is not None:
        existing = await users.find_one({"email": data["email"]})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "email": data["email"],
        "phone_number": phone,
        "full_name": full_name,
        "hashed_password": hash_password(data["password"]),
        "vouch_score": 100.0,
        "total_contracts": 0,
        "completed_as_customer": 0,
        "completed_as_provider": 0,
        "total_earned": 0,
        "total_spent": 0,
        "created_at": datetime.utcnow(),
        "last_mode": "customer"
    }

    if users is not None:
        result = await users.insert_one(user)
        user_id = str(result.inserted_id)
    else:
        user_id = str(len(_fallback_users) + 1)
        user["_id"] = user_id
        _fallback_users.append(user)

    return {
        "success": True,
        "message": "Account created! You can now login as Customer or Provider.",
        "data": {"user_id": user_id}
    }
@router.post("/login")
@limiter.limit("10/minute")
async def login_user(request: Request, data: dict):
    """
    Login with mode selection.
    Body: {email, password, mode: "customer"|"provider"}
    """
    mode = data.get("mode", "customer")
    if mode not in ["customer", "provider"]:
        raise HTTPException(status_code=400, detail="Mode must be 'customer' or 'provider'")

    users = await get_users_collection()
    user = None
    
    if users is not None:
        user = await users.find_one({"email": data["email"]})
    else:
        for u in _fallback_users:
            if u["email"] == data["email"]:
                user = u
                break

    if not user or not verify_password(data["password"], user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user.get("_id", user.get("id")))
    
    # Update last_mode in database
    if users is not None:
        from bson import ObjectId
        await users.update_one(
            {"_id": ObjectId(user_id) if isinstance(user.get("_id"), ObjectId) else user_id},
            {"$set": {"last_mode": mode}}
        )

    token = create_login_token(
        user_id=user_id,
        email=user["email"],
        mode=mode,
        phone=user.get("phone_number", ""),
        name=user.get("full_name", "User")
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "mode": mode,
        "user": {
            "id": user_id,
            "email": user["email"],
            "phone_number": user.get("phone_number", ""),
            "full_name": user.get("full_name", "User"),
            "vouch_score": user.get("vouch_score", 100.0),
            "total_contracts": user.get("total_contracts", 0),
            "completed_as_customer": user.get("completed_as_customer", 0),
            "completed_as_provider": user.get("completed_as_provider", 0),
            "current_mode": mode
        }
    }

@router.put("/switch-mode")
async def switch_mode(data: dict, current_user: dict = Depends(get_current_user)):
    """Switch between customer and provider mode without re-login"""
    new_mode = data.get("mode", "customer")
    if new_mode not in ["customer", "provider"]:
        raise HTTPException(status_code=400, detail="Mode must be 'customer' or 'provider'")
    
    # Create new token with new mode
    new_token = create_login_token(
        user_id=current_user["user_id"],
        email=current_user["email"],
        mode=new_mode,
        phone=current_user.get("phone", ""),
        name=current_user.get("name", "User")
    )
    
    return {
        "success": True,
        "message": f"Switched to {new_mode} mode",
        "access_token": new_token,
        "mode": new_mode
    }

@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]

    db = mongodb.get_db()
    if db is not None:
        try:
            from bson import ObjectId
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                return {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "phone_number": user.get("phone_number", ""),
                    "full_name": user.get("full_name", "User"),
                    "vouch_score": user.get("vouch_score", 100.0),
                    "total_contracts": user.get("total_contracts", 0),
                    "completed_as_customer": user.get("completed_as_customer", 0),
                    "completed_as_provider": user.get("completed_as_provider", 0),
                    "total_earned": user.get("total_earned", 0),
                    "total_spent": user.get("total_spent", 0),
                    "current_mode": current_user.get("mode", "customer")
                }
        except:
            pass

    raise HTTPException(status_code=404, detail="User not found")

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: dict):
    """Send password reset code via email OR WhatsApp"""
    email = data.get("email", "")
    phone = data.get("phone", "")
    method = data.get("method", "whatsapp")
    
    users = await get_users_collection()
    user = None
    
    if users is not None:
        if email:
            user = await users.find_one({"email": email})
        elif phone:
            user = await users.find_one({"phone_number": phone})
    
    if not user:
        return {"success": True, "message": "If account exists, reset instructions sent"}
    
    import random
    reset_code = str(random.randint(100000, 999999))
    
    if users is not None:
        from bson import ObjectId
        await users.update_one(
            {"_id": ObjectId(user["_id"])} if isinstance(user["_id"], str) else {"_id": user["_id"]},
            {"$set": {
                "reset_code": reset_code,
                "reset_code_expiry": str(datetime.utcnow() + timedelta(minutes=15))
                        }}
        )
    
    sent_via = ""          # ← 4 spaces, OUTSIDE the if block
    
    # Send via WhatsApp
    if method == "whatsapp":
        phone_num = user.get("phone_number", "")
        if phone_num:
            from core.messaging.whatsapp_bot import whatsapp_bot
            whatsapp_bot.send_message(
                phone_num,
                f"Dokets Password Reset Code: {reset_code}\nValid for 15 minutes."
            )
            sent_via = "WhatsApp"
    
    # Send via Email (safe)
        if method == "email" or (method == "whatsapp" and not sent_via):
        try:
            from core.messaging.email_notifications import email_notifier
            if email_notifier:
                email_notifier.send_email(
                    user["email"],
                    "Dokets - Password Reset Code",
                    f"<h2>Password Reset</h2><p>Your code: <strong>{reset_code}</strong></p>"
                )
                sent_via = "Email" if not sent_via else sent_via + " + Email"
            else:
                sent_via = "WhatsApp (email not configured)"
        except Exception as e:
            sent_via = "Email error: " + str(e)[:100]
    
    if not sent_via:
        sent_via = "No delivery method available. Code: " + reset_code
    
    return {"success": True, "message": f"Reset code sent via {sent_via}", "sent_via": sent_via}

@router.post("/reset-password")
@limiter.limit("3/minute")
async def reset_password(request: Request, data: dict):
    """Reset password using code"""
    email = data.get("email", "")
    code = data.get("code", "")
    new_password = data.get("new_password", "")
    
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    users = await get_users_collection()
    if users is not None:
        user = await users.find_one({"email": email})
        if not user or user.get("reset_code") != code:
            raise HTTPException(status_code=400, detail="Invalid reset code")
        
        expiry = user.get("reset_code_expiry")
        if expiry and datetime.utcnow() > datetime.fromisoformat(expiry):
            raise HTTPException(status_code=400, detail="Reset code expired")
        
        from bson import ObjectId
        uid = user["_id"]
        await users.update_one(
            {"_id": ObjectId(uid) if isinstance(uid, str) else uid},
            {"$set": {
                "hashed_password": hash_password(new_password),
                "reset_code": None,
                "reset_code_expiry": None
            }}
        )
    
    return {"success": True, "message": "Password reset successful! You can now login."}

_fallback_users = []