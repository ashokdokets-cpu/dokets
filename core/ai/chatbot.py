"""
Dokets VouchAI - AI-Powered Smart Chatbot
"""

import logging
import os
from config.settings import settings

logger = logging.getLogger("dokets.chatbot")

class DoketsChatbot:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-key":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("AI Chatbot initialized with OpenAI")
            except Exception as e:
                logger.warning(f"Chatbot OpenAI init failed: {e}")
        
        self.context = """
        You are Dokets VouchAI assistant. You help users with:
        - Creating AI-powered contracts with escrow protection
        - Understanding 1% platform fees
        - How escrow works (payment held until work verified)
        - Building Vouch Scores for reputation
        - Multi-currency support (13 currencies)
        - WhatsApp contract creation
        - KYC verification (13 ID types)
        - Dispute resolution with AI mediation
        - Instant payouts via UPI, bank, PayPal
        - Free video calls via Jitsi Meet
        - Background checks
        - White label agency mode
        - Recurring contracts
        
        Be friendly, concise, and helpful. Use emojis occasionally.
        If you don't know something, suggest visiting the Support tab or creating a ticket.
        """
    
    def get_response(self, question):
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": self.context},
                        {"role": "user", "content": question}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                answer = response.choices[0].message.content
                logger.info(f"Chatbot answered: {question[:30]}...")
                return {"response": answer, "source": "openai", "confidence": 0.95}
            except Exception as e:
                logger.error(f"OpenAI chatbot error: {e}")
        
        # Smart fallback without OpenAI
        return self._smart_fallback(question)
    
    def _smart_fallback(self, question):
        q = question.lower()
        
        responses = {
            "hello": "Hello! 👋 I'm Dokets AI assistant. How can I help you today?",
            "hi": "Hi there! 🛡️ Ready to create a trust-based contract?",
            "fee": "Dokets charges only **1% platform fee** per transaction. That's it! No hidden charges.",
            "escrow": "🔒 Payment is held securely in escrow. It's only released when AI verifies the work is done or the customer approves it.",
            "contract": "You can create a contract in 3 ways:\n1. 📝 New Contract tab - manual\n2. 🤖 AI Smart Contract - just describe the work\n3. 💬 WhatsApp - send a message!",
            "payment": "We support:\n💳 Razorpay (UPI/Cards)\n💰 PayPal\n📱 UPI\n💳 Stripe\n\nAll payments are secured in escrow.",
            "dispute": "⚖️ File a dispute from the Disputes tab. Our AI mediator will analyze the situation and propose a fair resolution within 24 hours.",
            "kyc": "🆔 Submit your ID from the KYC tab. We support 13+ ID types globally including Aadhaar, Passport, SSN, CPF, and more.",
            "payout": "⚡ Instant payout via UPI\n🏦 Bank transfer (1-2 days)\n💰 PayPal (3-5 days)\n\nOnly 1% fee!",
            "vouch": "⭐ Your Vouch Score builds with every completed contract. Higher scores = more trust = more jobs!",
            "whatsapp": "💬 Send 'NEW CONTRACT [description]' to our WhatsApp number to create contracts via chat!",
            "video": "📹 Free video calls via Jitsi Meet. Go to Video Calls tab, enter contract ID, and start!",
        }
        
        for keyword, answer in responses.items():
            if keyword in q:
                return {"response": answer, "source": "knowledge_base"}
        
        return {"response": "I'm here to help! You can ask me about contracts, escrow, payments, disputes, or any Dokets feature. You can also check our FAQs in the Support tab or create a ticket. 😊", "source": "fallback"}

chatbot = DoketsChatbot()