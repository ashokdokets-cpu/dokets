"""
Dokets VouchAI - White Label / Agency Mode
"""

import logging
from datetime import datetime

logger = logging.getLogger("dokets.whitelabel")

class WhiteLabel:
    def __init__(self):
        self.agencies = []
        logger.info("White label engine ready")
    
    def create_agency(self, owner_id, name, domain, settings=None):
        agency = {
            "id": f"AG-{len(self.agencies)+1:04d}",
            "owner_id": owner_id,
            "name": name,
            "domain": domain,
            "branding": {
                "logo": settings.get("logo", ""),
                "primary_color": settings.get("primary_color", "#4F46E5"),
                "company_name": name,
                "custom_domain": domain
            },
            "settings": settings or {},
            "users": [owner_id],
            "contracts": [],
            "created_at": str(datetime.utcnow()),
            "status": "active",
            "plan": settings.get("plan", "free")
        }
        self.agencies.append(agency)
        logger.info(f"Agency created: {name} ({domain})")
        return agency
    
    def get_agency(self, agency_id):
        for a in self.agencies:
            if a["id"] == agency_id:
                return a
        return None
    
    def add_user_to_agency(self, agency_id, user_id):
        for a in self.agencies:
            if a["id"] == agency_id:
                a["users"].append(user_id)
                return a
        return None

whitelabel = WhiteLabel()