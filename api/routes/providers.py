"""
Dokets VouchAI - Provider Discovery & Reusability
"""

from fastapi import APIRouter, Depends
from core.security.auth import get_current_user
_users = []  # Will be populated from MongoDB
from api.routes.contracts import _contracts
from core.database.mongodb import mongodb
from datetime import datetime

router = APIRouter(prefix="/api/v1/providers", tags=["Providers"])

SERVICE_CATEGORIES = [
    {"id": "home", "name": "🏠 Home Services", "icon": "🏠", "skills": ["Painting", "Plumbing", "Electrical", "Cleaning", "Carpentry", "AC Repair", "Masonry", "Waterproofing", "Pest Control", "Interior Design"]},
    {"id": "tech", "name": "💻 Tech & IT", "icon": "💻", "skills": ["Web Development", "App Development", "Graphic Design", "Video Editing", "Data Entry", "SEO", "WordPress", "Cybersecurity", "Cloud Services"]},
    {"id": "transport", "name": "🚗 Transport & Logistics", "icon": "🚗", "skills": ["Cab Service", "Bike Transport", "Truck Transport", "Packers & Movers", "Courier", "Food Delivery"]},
    {"id": "education", "name": "📚 Education & Training", "icon": "📚", "skills": ["Tutoring", "Exam Prep", "Music Lessons", "Yoga Training", "Language Classes", "Coding Classes", "Dance Classes"]},
    {"id": "events", "name": "🎉 Events & Entertainment", "icon": "🎉", "skills": ["Photography", "Catering", "Decoration", "DJ Service", "Event Planning", "Makeup Artist", "Mehendi", "Balloon Decoration"]},
    {"id": "health", "name": "🏥 Health & Wellness", "icon": "🏥", "skills": ["Physiotherapy", "Massage", "Diet Planning", "Personal Training", "Counselling", "Yoga", "Meditation"]},
    {"id": "business", "name": "💼 Business & Finance", "icon": "💼", "skills": ["Accounting", "Legal Advice", "Marketing", "Content Writing", "Tax Filing", "Company Registration", "GST Filing"]},
    {"id": "auto", "name": "🔧 Auto Services", "icon": "🔧", "skills": ["Car Repair", "Bike Repair", "Car Wash", "Tyre Service", "Battery Service", "Car Detailing", "Windshield Repair"]},
    {"id": "beauty", "name": "💅 Beauty & Personal Care", "icon": "💅", "skills": ["Hair Styling", "Spa Service", "Nail Art", "Bridal Makeup", "Mehendi", "Facial", "Waxing"]},
    {"id": "realestate", "name": "🏠 Real Estate", "icon": "🏠", "skills": ["Property Listing", "Rental Agent", "Property Inspection", "Interior Design", "Vastu Consultation"]},
    {"id": "other", "name": "📦 Other Services", "icon": "📦", "skills": ["Custom Service", "Anything Else"]},
]

@router.get("/search")
async def search_providers(service: str = "", location: str = "", min_score: float = 70):
    """Search providers by service, location, and minimum vouch score"""
    results = []
    for u in _users:
        if u.get("user_role") == "service_provider" and u.get("vouch_score", 0) >= min_score:
            # Get their completed contracts
            completed = len([c for c in _contracts if c.get("provider_id") == u["id"] and c.get("status") == "completed"])
            if completed > 0:
                results.append({
                    "id": u["id"],
                    "name": u.get("full_name", "Unknown"),
                    "phone": u.get("phone_number", ""),
                    "vouch_score": u.get("vouch_score", 100),
                    "completed_contracts": completed,
                    "location": location or "Available",
                    "service": service or "General"
                })
    
    return {"providers": sorted(results, key=lambda x: x["vouch_score"], reverse=True)}

@router.get("/top-rated")
async def top_rated_providers():
    """Get top rated providers for reuse"""
    providers = []
    for u in _users:
        if u.get("user_role") == "service_provider":
            completed = len([c for c in _contracts if c.get("provider_id") == u["id"] and c.get("status") == "completed"])
            if completed > 0:
                providers.append({
                    "id": u["id"],
                    "name": u.get("full_name"),
                    "vouch_score": u.get("vouch_score", 100),
                    "total_done": completed,
                    "rehire_rate": "95%",
                    "badge": "Diamond" if u.get("vouch_score", 0) >= 95 else "Gold" if u.get("vouch_score", 0) >= 80 else "Silver"
                })
    
    return {"top_providers": sorted(providers, key=lambda x: x["vouch_score"], reverse=True)[:10]}

@router.get("/my-providers")
async def my_providers(current_user: dict = Depends(get_current_user)):
    """Providers I've worked with before (for rehiring)"""
    my_contracts = [c for c in _contracts if c.get("customer_id") == current_user["user_id"]]
    provider_ids = set(c.get("provider_id") for c in my_contracts if c.get("provider_id"))
    
    providers = []
    for pid in provider_ids:
        user = next((u for u in _users if u["id"] == pid), None)
        if user:
            completed = len([c for c in my_contracts if c.get("provider_id") == pid and c.get("status") == "completed"])
            providers.append({
                "id": user["id"],
                "name": user.get("full_name"),
                "vouch_score": user.get("vouch_score", 100),
                "times_hired": completed,
                "last_contract": max((c.get("created_at", "") for c in my_contracts if c.get("provider_id") == pid), default="")
            })
    
    return {"my_providers": sorted(providers, key=lambda x: x["times_hired"], reverse=True)}


@router.put("/profile")
async def update_provider_profile(data: dict, current_user: dict = Depends(get_current_user)):
    """Provider updates their service profile with skills, rates, portfolio"""
    db = mongodb.get_db()
    
    skills = data.get("skills", [])
    categories = data.get("categories", [])
    
    # Auto-assign uncategorized skills to "other" category
    all_known_skills = []
    for cat in SERVICE_CATEGORIES:
        all_known_skills.extend([s.lower() for s in cat["skills"]])
    
    has_unknown_skill = False
    for skill in skills:
        if skill.lower() not in all_known_skills:
            has_unknown_skill = True
            break
    
    # If provider has skills not in any category, add "other" category
    if has_unknown_skill and "other" not in categories:
        categories.append("other")
    
    # If provider selected categories but no skills, auto-suggest based on categories
    if not skills and categories:
        suggested_skills = []
        for cat in SERVICE_CATEGORIES:
            if cat["id"] in categories:
                suggested_skills.extend(cat["skills"][:3])  # Top 3 skills per category
        skills = suggested_skills[:5]  # Max 5 suggested skills
    
    profile = {
        "user_id": current_user["user_id"],
        "skills": skills,
        "categories": categories,
        "experience_years": data.get("experience_years", 0),
        "hourly_rate": data.get("hourly_rate", 0),
        "bio": data.get("bio", ""),
        "portfolio": data.get("portfolio", []),
        "languages": data.get("languages", ["English"]),
        "availability": data.get("availability", "available"),
        "service_cities": data.get("service_cities", []),
        "updated_at": str(datetime.utcnow())
    }
    
    if db is not None:
        await db.provider_profiles.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": profile},
            upsert=True
        )
    
    return {"success": True, "message": "Profile updated!", "profile": profile}


@router.get("/profile/{user_id}")
async def get_provider_profile(user_id: str):
    """Get a provider's full profile"""
    db = mongodb.get_db()
    if db is not None:
        profile = await db.provider_profiles.find_one({"user_id": user_id})
        if profile:
            profile["_id"] = str(profile["_id"])
            return {"success": True, "profile": profile}
    
    return {"success": False, "message": "Profile not found"}


@router.get("/categories")
async def get_service_categories():
    """Get all service categories"""
    return {"categories": SERVICE_CATEGORIES}


@router.get("/by-category/{category_id}")
async def providers_by_category(category_id: str):
    """Get providers in a specific category"""
    db = mongodb.get_db()
    results = []
    
    if db is not None:
        profiles = await db.provider_profiles.find({
            "categories": category_id
        }).to_list(length=50)
        
        for p in profiles:
            p["_id"] = str(p["_id"])
            # Get user info
            user = await db.users.find_one({"_id": p["user_id"]}) if "_id" in p else None
            results.append({
                "id": p["user_id"],
                "name": user.get("full_name", "Provider") if user else "Provider",
                "vouch_score": user.get("vouch_score", 100) if user else 100,
                "skills": p.get("skills", []),
                "hourly_rate": p.get("hourly_rate", 0),
                "bio": p.get("bio", ""),
                "availability": p.get("availability", "available"),
                "experience_years": p.get("experience_years", 0)
            })
    
    return {"providers": sorted(results, key=lambda x: x["vouch_score"], reverse=True)}


@router.get("/by-skill/{skill}")
async def providers_by_skill(skill: str):
    """Search providers by specific skill"""
    db = mongodb.get_db()
    results = []
    
    if db is not None:
        profiles = await db.provider_profiles.find({
            "skills": {"$regex": skill, "$options": "i"}
        }).to_list(length=50)
        
        for p in profiles:
            p["_id"] = str(p["_id"])
            results.append({
                "id": p["user_id"],
                "skills": p.get("skills", []),
                "hourly_rate": p.get("hourly_rate", 0),
                "bio": p.get("bio", ""),
                "availability": p.get("availability", "available")
            })
    
    return {"providers": results}

@router.put("/packages")
async def update_service_packages(data: dict, current_user: dict = Depends(get_current_user)):
    """Provider sets their service packages (Basic/Standard/Premium)"""
    db = mongodb.get_db()
    
    packages = {
        "basic": data.get("basic", {"name": "Basic", "price": 0, "description": "", "delivery_days": 1}),
        "standard": data.get("standard", {"name": "Standard", "price": 0, "description": "", "delivery_days": 3}),
        "premium": data.get("premium", {"name": "Premium", "price": 0, "description": "", "delivery_days": 7}),
        "updated_at": str(datetime.utcnow())
    }
    
    if db is not None:
        await db.provider_profiles.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": {"packages": packages}},
            upsert=True
        )
    
    return {"success": True, "message": "Packages updated!", "packages": packages}

@router.get("/packages/{user_id}")
async def get_provider_packages(user_id: str):
    """Get provider's service packages"""
    db = mongodb.get_db()
    if db is not None:
        profile = await db.provider_profiles.find_one({"user_id": user_id})
        if profile and profile.get("packages"):
            return {"success": True, "packages": profile["packages"]}
    return {"success": False, "packages": None}

@router.get("/my-profile")
async def my_provider_profile(current_user: dict = Depends(get_current_user)):
    """Get my own provider profile"""
    db = mongodb.get_db()
    if db is not None:
        profile = await db.provider_profiles.find_one({"user_id": current_user["user_id"]})
        if profile:
            profile["_id"] = str(profile["_id"])
            return {"success": True, "profile": profile}
    return {"success": False, "message": "Profile not found"}