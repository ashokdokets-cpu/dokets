"""
Dokets VouchAI - Input Validation & Security
"""
import re
from typing import Tuple

class SecurityValidator:
    @staticmethod
    def sanitize_string(text: str) -> str:
        """Remove XSS, SQL injection attempts"""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        # Remove script attempts
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        # Remove SQL injection patterns
        text = re.sub(r"(\bSELECT\b|\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b)", '', text, flags=re.IGNORECASE)
        # Limit length
        return text[:1000]
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        if len(email) > 100:
            return False, "Email too long"
        return True, email.lower().strip()
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number"""
        # Remove spaces, dashes, parentheses
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        if not phone.startswith('+'):
            phone = '+' + phone
        if not re.match(r'^\+\d{7,15}$', phone):
            return False, "Invalid phone number"
        return True, phone
    
    @staticmethod
    def validate_amount(amount: float) -> Tuple[bool, str]:
        """Validate transaction amount"""
        if amount <= 0:
            return False, "Amount must be positive"
        if amount > 10000000:  # 1 crore limit
            return False, "Amount exceeds maximum limit"
        return True, round(amount, 2)
    
    @staticmethod
    def detect_bot(user_agent: str, ip: str) -> bool:
        """Detect common bot patterns"""
        bot_patterns = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python-requests']
        if user_agent:
            user_agent_lower = user_agent.lower()
            for pattern in bot_patterns:
                if pattern in user_agent_lower:
                    return True
        return False

security = SecurityValidator()