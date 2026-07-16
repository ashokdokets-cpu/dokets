"""
Dokets VouchAI - Reviews & Ratings System
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from core.security.auth import get_current_user
from core.database.mongodb import mongodb

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])

@router.post("/submit")
async def submit_review(data: dict, current_user: dict = Depends(get_current_user)):
    """Submit a review after contract completion"""
    db = mongodb.get_db()
    
    contract_id = data.get("contract_id")
    rating = data.get("rating", 5)  # 1-5 stars
    review_text = data.get("review", "")
    
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    
    review = {
        "contract_id": contract_id,
        "reviewer_id": current_user["user_id"],
        "reviewer_name": current_user.get("name", "User"),
        "rating": rating,
        "review": review_text,
        "created_at": str(datetime.utcnow())
    }
    
    if db is not None:
        # Get contract to find the other party
        contract = await db.contracts.find_one({"id": contract_id})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Determine who is being reviewed
        if current_user["user_id"] == contract.get("customer_id"):
            reviewed_id = contract.get("provider_id")
            review["review_type"] = "customer_to_provider"
        else:
            reviewed_id = contract.get("customer_id")
            review["review_type"] = "provider_to_customer"
        
        review["reviewed_id"] = reviewed_id
        
        await db.reviews.insert_one(review)
        
        # Update user's average rating
        await update_user_rating(db, reviewed_id)
        
        # Update contract as reviewed
        await db.contracts.update_one(
            {"id": contract_id},
            {"$set": {"reviewed": True, "reviewed_at": str(datetime.utcnow())}}
        )
    
    return {"success": True, "message": "Review submitted!", "review": review}


@router.get("/user/{user_id}")
async def get_user_reviews(user_id: str):
    """Get all reviews for a user"""
    db = mongodb.get_db()
    if db is not None:
        reviews = await db.reviews.find({"reviewed_id": user_id}).sort("created_at", -1).to_list(length=50)
        for r in reviews:
            r["_id"] = str(r["_id"])
        
        avg_rating = 0
        if reviews:
            avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1)
        
        return {
            "reviews": reviews,
            "total": len(reviews),
            "average_rating": avg_rating
        }
    return {"reviews": [], "total": 0, "average_rating": 0}


@router.get("/contract/{contract_id}")
async def get_contract_review(contract_id: str, current_user: dict = Depends(get_current_user)):
    """Check if current user already reviewed this contract"""
    db = mongodb.get_db()
    if db is not None:
        review = await db.reviews.find_one({
            "contract_id": contract_id,
            "reviewer_id": current_user["user_id"]
        })
        if review:
            review["_id"] = str(review["_id"])
            return {"reviewed": True, "review": review}
    return {"reviewed": False}


async def update_user_rating(db, user_id: str):
    """Update user's average rating"""
    from bson import ObjectId
    reviews = await db.reviews.find({"reviewed_id": user_id}).to_list(length=100)
    if reviews:
        avg = round(sum(r["rating"] for r in reviews) / len(reviews), 1)
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"rating": avg, "total_reviews": len(reviews)}}
        )