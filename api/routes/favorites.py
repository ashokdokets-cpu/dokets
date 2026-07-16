"""
Dokets VouchAI - Saved/Favorite Providers
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from core.security.auth import get_current_user
from core.database.mongodb import mongodb

router = APIRouter(prefix="/api/v1/favorites", tags=["Favorites"])

@router.post("/add/{provider_id}")
async def add_favorite(provider_id: str, current_user: dict = Depends(get_current_user)):
    """Bookmark a provider for rehire"""
    db = mongodb.get_db()
    
    fav = {
        "user_id": current_user["user_id"],
        "provider_id": provider_id,
        "saved_at": str(datetime.utcnow())
    }
    
    if db is not None:
        existing = await db.favorites.find_one({
            "user_id": current_user["user_id"],
            "provider_id": provider_id
        })
        if existing:
            return {"success": True, "message": "Already saved"}
        
        await db.favorites.insert_one(fav)
    
    return {"success": True, "message": "Provider saved to favorites!"}


@router.delete("/remove/{provider_id}")
async def remove_favorite(provider_id: str, current_user: dict = Depends(get_current_user)):
    """Remove from favorites"""
    db = mongodb.get_db()
    if db is not None:
        await db.favorites.delete_one({
            "user_id": current_user["user_id"],
            "provider_id": provider_id
        })
    return {"success": True, "message": "Removed from favorites"}


@router.get("/list")
async def my_favorites(current_user: dict = Depends(get_current_user)):
    """Get my saved providers with details"""
    db = mongodb.get_db()
    if db is not None:
        favs = await db.favorites.find({"user_id": current_user["user_id"]}).to_list(length=50)
        
        providers = []
        for fav in favs:
            from bson import ObjectId
            user = await db.users.find_one({"_id": ObjectId(fav["provider_id"])})
            profile = await db.provider_profiles.find_one({"user_id": fav["provider_id"]})
            
            if user:
                providers.append({
                    "id": fav["provider_id"],
                    "name": user.get("full_name", "Provider"),
                    "vouch_score": user.get("vouch_score", 100),
                    "rating": user.get("rating", 0),
                    "skills": profile.get("skills", []) if profile else [],
                    "hourly_rate": profile.get("hourly_rate", 0) if profile else 0,
                    "saved_at": fav["saved_at"]
                })
        
        return {"favorites": providers, "total": len(providers)}
    
    return {"favorites": [], "total": 0}


@router.get("/check/{provider_id}")
async def is_favorite(provider_id: str, current_user: dict = Depends(get_current_user)):
    """Check if provider is saved"""
    db = mongodb.get_db()
    if db is not None:
        fav = await db.favorites.find_one({
            "user_id": current_user["user_id"],
            "provider_id": provider_id
        })
        return {"saved": fav is not None}
    return {"saved": False}