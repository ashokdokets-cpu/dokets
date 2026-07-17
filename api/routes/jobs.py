"""
Dokets VouchAI - Public Job Board
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from core.security.auth import get_current_user
from core.database.mongodb import mongodb

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])

@router.post("/post")
async def post_job(data: dict, current_user: dict = Depends(get_current_user)):
    """Post a public job that providers can browse and apply to"""
    db = mongodb.get_db()
    
    job = {
        "id": f"JOB-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "title": data.get("title"),
        "description": data.get("description", ""),
        "category": data.get("category", "other"),
        "skills_required": data.get("skills_required", []),
        "budget_min": data.get("budget_min", 0),
        "budget_max": data.get("budget_max", 0),
        "currency": data.get("currency", "INR"),
        "location": data.get("location", "Remote"),
        "posted_by": current_user["user_id"],
        "poster_name": current_user.get("name", "User"),
        "status": "open",
        "applications": [],
        "created_at": str(datetime.utcnow()),
        "deadline": data.get("deadline", "")
    }
    if db is not None:
        result = await db.jobs.insert_one(job)
        job["_id"] = str(result.inserted_id)
    
    return {"success": True, "message": "Job posted!", "job": job}


@router.get("/list")
async def list_jobs(category: str = "", status: str = "open"):
    """List all open jobs publicly"""
    db = mongodb.get_db()
    query = {"status": status}
    if category:
        query["category"] = category
    
    if db is not None:
        jobs = await db.jobs.find(query).sort("created_at", -1).to_list(length=50)
        for j in jobs:
            j["_id"] = str(j["_id"])
        return {"jobs": jobs, "total": len(jobs)}
    
    return {"jobs": [], "total": 0}


@router.get("/my-jobs")
async def my_posted_jobs(current_user: dict = Depends(get_current_user)):
    """Jobs I've posted"""
    db = mongodb.get_db()
    if db is not None:
        jobs = await db.jobs.find({"posted_by": current_user["user_id"]}).sort("created_at", -1).to_list(length=50)
        for j in jobs:
            j["_id"] = str(j["_id"])
        return {"jobs": jobs, "total": len(jobs)}
    return {"jobs": [], "total": 0}


@router.post("/{job_id}/apply")
async def apply_to_job(job_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Provider applies to a job"""
    db = mongodb.get_db()
    
    application = {
        "provider_id": current_user["user_id"],
        "provider_name": current_user.get("name", "Provider"),
        "cover_letter": data.get("cover_letter", ""),
        "bid_amount": data.get("bid_amount", 0),
        "applied_at": str(datetime.utcnow())
    }
    
    if db is not None:
        await db.jobs.update_one(
            {"id": job_id},
            {"$push": {"applications": application}}
        )
    
    return {"success": True, "message": "Applied successfully!"}

@router.get("/categories")
async def job_categories():
    return {
        "categories": [
            {"id": "home", "name": "🏠 Home Services", "icon": "🏠"},
            {"id": "tech", "name": "💻 Tech & IT", "icon": "💻"},
            {"id": "transport", "name": "🚗 Transport", "icon": "🚗"},
            {"id": "education", "name": "📚 Education", "icon": "📚"},
            {"id": "events", "name": "🎉 Events", "icon": "🎉"},
            {"id": "health", "name": "🏥 Health", "icon": "🏥"},
            {"id": "business", "name": "💼 Business", "icon": "💼"},
            {"id": "auto", "name": "🔧 Auto", "icon": "🔧"},
            {"id": "other", "name": "📦 Other", "icon": "📦"},
        ]
    }