"""
Dokets VouchAI - Contract Templates Library
"""
from fastapi import APIRouter, Depends
from core.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/templates", tags=["Templates"])

CONTRACT_TEMPLATES = [
    {"id":"painting","name":"🏠 House Painting","category":"home","title":"House Painting Service","description":"Professional painting service for your home","milestones":[{"title":"Surface Preparation","amount_pct":30},{"title":"Painting Work","amount_pct":50},{"title":"Final Touch-up","amount_pct":20}],"estimated_amount":15000},
    {"id":"plumbing","name":"🔧 Plumbing Repair","category":"home","title":"Plumbing Repair Service","description":"Expert plumbing repair and installation","milestones":[{"title":"Inspection & Quote","amount_pct":10},{"title":"Repair Work","amount_pct":70},{"title":"Testing & Cleanup","amount_pct":20}],"estimated_amount":5000},
    {"id":"cleaning","name":"🧹 House Cleaning","category":"home","title":"House Cleaning Service","description":"Complete house cleaning service","milestones":[{"title":"Deep Clean","amount_pct":50},{"title":"Final Inspection","amount_pct":50}],"estimated_amount":3000},
    {"id":"webdev","name":"💻 Web Development","category":"tech","title":"Website Development","description":"Professional website development","milestones":[{"title":"Design & Planning","amount_pct":30},{"title":"Development","amount_pct":50},{"title":"Testing & Launch","amount_pct":20}],"estimated_amount":25000},
    {"id":"appdev","name":"📱 App Development","category":"tech","title":"Mobile App Development","description":"iOS/Android app development","milestones":[{"title":"UI/UX Design","amount_pct":25},{"title":"Development","amount_pct":50},{"title":"Testing & Deployment","amount_pct":25}],"estimated_amount":50000},
    {"id":"photography","name":"📸 Photography","category":"events","title":"Photography Service","description":"Professional photography for events","milestones":[{"title":"Event Coverage","amount_pct":70},{"title":"Photo Delivery","amount_pct":30}],"estimated_amount":10000},
    {"id":"tutoring","name":"📚 Tutoring","category":"education","title":"Online Tutoring","description":"One-on-one tutoring sessions","milestones":[{"title":"First Session","amount_pct":25},{"title":"Mid-term Review","amount_pct":25},{"title":"Final Session","amount_pct":50}],"estimated_amount":8000},
    {"id":"catering","name":"🍽️ Catering","category":"events","title":"Catering Service","description":"Food catering for events","milestones":[{"title":"Menu Planning","amount_pct":20},{"title":"Food Preparation","amount_pct":50},{"title":"Service & Cleanup","amount_pct":30}],"estimated_amount":20000},
]

@router.get("/list")
async def list_templates(category: str = ""):
    if category:
        return {"templates": [t for t in CONTRACT_TEMPLATES if t["category"] == category]}
    return {"templates": CONTRACT_TEMPLATES}

@router.get("/categories")
async def template_categories():
    cats = list(set(t["category"] for t in CONTRACT_TEMPLATES))
    return {"categories": [{"id":c,"name":c.title(),"count":len([t for t in CONTRACT_TEMPLATES if t["category"]==c])} for c in cats]}

@router.get("/{template_id}")
async def get_template(template_id: str):
    for t in CONTRACT_TEMPLATES:
        if t["id"] == template_id:
            return {"success": True, "template": t}
    return {"success": False, "message": "Template not found"}