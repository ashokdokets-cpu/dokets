from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from core.security.auth import hash_password, verify_password, create_access_token, get_current_user
from core.database.mongodb import mongodb

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.post("/register")
async def register_user(data: dict):
    collection = mongodb.get_collection("users")
    
    # Check existing - with error handling
    if collection:
        try:
            existing = await collection.find_one({"email": data["email"]})
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
        except:
            collection = None  # Fallback to in-memory
    
    user = {
        "email": data["email"],
        "phone_number": data.get("phone_number", ""),
        "full_name": data.get("full_name", "User"),
        "hashed_password": hash_password(data["password"]),
        "user_role": data.get("user_role", "customer"),
        "vouch_score": 100.0,
        "total_contracts": 0,
        "created_at": datetime.utcnow()
    }
    
    if collection:
        try:
            result = await collection.insert_one(user)
            user_id = str(result.inserted_id)
        except:
            _fallback_users.append(user)
            user_id = str(len(_fallback_users))
    else:
        _fallback_users.append(user)
        user_id = str(len(_fallback_users))
    
    return {"success": True, "message": "User registered", "data": {"user_id": user_id}}

@router.post("/login")
async def login_user(data: dict):
    collection = mongodb.get_collection("users")
    
    user = None
    if collection:
        user = await collection.find_one({"email": data["email"]})
    else:
        for u in _fallback_users:
            if u["email"] == data["email"]:
                user = u
                break
    
    if not user or not verify_password(data["password"], user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id = str(user.get("_id", user.get("id")))
    token = create_access_token(data={"sub": user_id, "email": user["email"]})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user["email"],
            "phone_number": user.get("phone_number", ""),
            "full_name": user.get("full_name", "User"),
            "user_role": user.get("user_role", "customer"),
            "vouch_score": user.get("vouch_score", 100.0),
            "total_contracts": user.get("total_contracts", 0)
        }
    }

@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    collection = mongodb.get_collection("users")
    user_id = current_user["user_id"]
    
    user = None
    if collection:
        from bson import ObjectId
        try:
            user = await collection.find_one({"_id": ObjectId(user_id)})
        except:
            pass
    
    if not user:
        for u in _fallback_users:
            if u.get("id") == user_id:
                user = u
                break
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user.get("_id", user.get("id"))),
        "email": user["email"],
        "phone_number": user.get("phone_number", ""),
        "full_name": user.get("full_name", "User"),
        "user_role": user.get("user_role", "customer"),
        "vouch_score": user.get("vouch_score", 100.0),
        "total_contracts": user.get("total_contracts", 0)
    }

# Fallback storage
_fallback_users = []