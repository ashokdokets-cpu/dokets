from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
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

_fallback_users = []