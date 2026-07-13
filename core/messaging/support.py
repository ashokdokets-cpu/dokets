"""
Dokets VouchAI - Support Ticket System
"""

import logging
from datetime import datetime

logger = logging.getLogger("dokets.support")

class SupportSystem:
    def __init__(self):
        self.tickets = []
        self.faqs = [
            {"q": "How does escrow work?", "a": "Payment is held securely until work is verified by AI or both parties agree."},
            {"q": "What are the fees?", "a": "Only 1% platform fee per transaction."},
            {"q": "How to file a dispute?", "a": "Go to Disputes tab and file with your contract ID."},
            {"q": "How long do payouts take?", "a": "Instant for UPI, 1-3 business days for bank transfers."},
            {"q": "Is my money safe?", "a": "Yes! Funds are held in secure escrow until work completion is verified."},
        ]
        logger.info("Support system ready")
    
    def create_ticket(self, user_id, subject, message, priority="normal"):
        ticket = {
            "id": f"TKT-{len(self.tickets)+1:04d}",
            "user_id": user_id,
            "subject": subject,
            "message": message,
            "priority": priority,
            "status": "open",
            "replies": [],
            "created_at": str(datetime.utcnow()),
            "updated_at": str(datetime.utcnow())
        }
        self.tickets.append(ticket)
        return ticket
    
    def reply_ticket(self, ticket_id, user_id, message):
        for t in self.tickets:
            if t["id"] == ticket_id:
                t["replies"].append({"user_id": user_id, "message": message, "time": str(datetime.utcnow())})
                t["updated_at"] = str(datetime.utcnow())
                return t
        return None
    
    def get_faqs(self):
        return self.faqs
    
    def search_faqs(self, query):
        query = query.lower()
        return [f for f in self.faqs if query in f["q"].lower() or query in f["a"].lower()]

support = SupportSystem()