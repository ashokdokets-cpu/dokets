"""
Dokets VouchAI - AI Support Chatbot
"""

import logging

logger = logging.getLogger("dokets.chatbot")

class DoketsChatbot:
    def __init__(self):
        self.faqs = {
            "fees": "Dokets charges only 1% platform fee per transaction.",
            "escrow": "Payment is held securely until work is verified by AI or approved by the customer.",
            "dispute": "File a dispute from the Disputes tab. Our AI mediator will help resolve it within 24 hours.",
            "payout": "Payouts are instant via UPI, 1-2 days via bank transfer, 3-5 days via PayPal.",
            "kyc": "Submit your ID from the KYC tab. We support 13+ ID types globally.",
        }
    
    def get_response(self, question):
        question_lower = question.lower()
        
        for keyword, answer in self.faqs.items():
            if keyword in question_lower:
                return {"response": answer, "source": "faq", "confidence": 0.9}
        
        # Default AI-like responses
        if "hello" in question_lower or "hi" in question_lower:
            return {"response": "Hello! I'm the Dokets assistant. How can I help you today?", "source": "greeting"}
        
        if "contract" in question_lower:
            return {"response": "You can create a contract from the New Contract tab, or use AI Smart Contract to generate one automatically!", "source": "knowledge"}
        
        if "payment" in question_lower:
            return {"response": "We support Razorpay, PayPal, UPI, and Stripe. Your payment is secured in escrow.", "source": "knowledge"}
        
        return {"response": "I'm here to help! You can also check our FAQs in the Support tab, or create a ticket for detailed assistance.", "source": "fallback"}

chatbot = DoketsChatbot()