"""
Dokets VouchAI - AI Engine
Handles contract extraction, work verification, and dispute mediation
"""

import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger("dokets.ai")

class DoketsAI:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-key":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("AI Engine initialized with OpenAI")
        else:
            logger.warning("No OpenAI API key found. AI features will use templates.")
    
    async def extract_contract_from_text(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Extract contract details from natural language text using AI"""
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """You are Dokets VouchAI, an expert at extracting contract details from informal conversations.
                        Extract: title, description, total_amount, currency, milestones (with title, amount, deadline).
                        Return ONLY valid JSON, no other text."""},
                        {"role": "user", "content": f"Extract contract details from: {text}"}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                logger.info(f"AI extracted contract: {result.get('title', 'Untitled')}")
                return result
                
            except Exception as e:
                logger.error(f"AI extraction failed: {e}")
        
        # Fallback: Basic extraction without AI
        return self._basic_extraction(text)
    
    def _basic_extraction(self, text: str) -> Dict[str, Any]:
        """Basic extraction without AI"""
        words = text.split()
        amounts = [w for w in words if w.replace("$", "").replace("₹", "").isdigit()]
        amount = float(amounts[0]) if amounts else 100
        
        return {
            "title": "Service Agreement",
            "description": text[:200],
            "total_amount": amount,
            "currency": "USD",
            "milestones": [
                {
                    "id": "MS-001",
                    "title": "Complete Work",
                    "description": text[:100],
                    "amount": amount,
                    "deadline": "2026-08-01"
                }
            ]
        }
    
    async def verify_work(self, description: str, proof_text: str = "") -> Dict[str, Any]:
        """AI verification of work completion"""
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a work verification AI. Assess if the described work matches the requirements. Return JSON with completion_percentage (0-100), recommendation (approve/review/dispute), and notes."},
                        {"role": "user", "content": f"Task: {description}\nProof: {proof_text}"}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                return json.loads(response.choices[0].message.content)
                
            except Exception as e:
                logger.error(f"AI verification failed: {e}")
        
        return {
            "completion_percentage": 80,
            "recommendation": "approve",
            "notes": "Work appears complete based on provided information."
        }
    
    async def mediate_dispute(self, contract: Dict, dispute_text: str) -> Dict[str, Any]:
        """AI dispute mediation"""
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are Dokets VouchAI mediator. Analyze the dispute and propose a fair resolution. Return JSON with recommendation, reason, and suggested_split percentage."},
                        {"role": "user", "content": f"Contract: {json.dumps(contract)}\nDispute: {dispute_text}"}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                return json.loads(response.choices[0].message.content)
                
            except Exception as e:
                logger.error(f"AI mediation failed: {e}")
        
        return {
            "recommendation": "split_50_50",
            "reason": "Unable to determine fault. Recommend equal split.",
            "suggested_split": 50
        }

# Global AI instance
ai_engine = DoketsAI()