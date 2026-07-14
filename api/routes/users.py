from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from core.security.auth import hash_password, verify_password, create_access_token, get_current_user
from core.database.mongodb import mongodb

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

async def get_users_collection():
    db = mongodb.get_db()
    if db is not None:
        return db.users
    return None

@router.post("/register")
async def register_user(data: dict):
    users = await get_users_collection()
    
    if users is not None:
        existing = await users.find_one({"email": data["email"]})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    
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
    
    if users is not None:
        result = await users.insert_one(user)
        user_id = str(result.inserted_id)
    else:
        user_id = str(len(_fallback_users) + 1)
        user["id"] = user_id
        _fallback_users.append(user)
    
    return {"success": True, "message": "User registered", "data": {"user_id": user_id}}

@router.post("/login")
async def login_user(data: dict):
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
    user_id = current_user["user_id"]
    users = await get_users_collection()
    
    user = None
    if users is not None:
        from bson import ObjectId
        try:
            user = await users.find_one({"_id": ObjectId(user_id)})
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

_fallback_users = []