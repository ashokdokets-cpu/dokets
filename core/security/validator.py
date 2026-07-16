"""
Dokets VouchAI - Input Validation & Security
"""
import re
from typing import Tuple

class SecurityValidator:
    # Known disposable email domains
    DISPOSABLE_DOMAINS = [
        'mailinator.com', 'guerrillamail.com', '10minutemail.com', 'tempmail.com',
        'throwaway.email', 'sharklasers.com', 'yopmail.com', 'trashmail.com'
    ]

    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Remove XSS, SQL injection, and other attacks"""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        # Remove script handlers
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'vbscript:', '', text, flags=re.IGNORECASE)
        # Remove SQL injection patterns
        dangerous_sql = [r'\bSELECT\b', r'\bDROP\b', r'\bDELETE\b', r'\bINSERT\b', 
                        r'\bUPDATE\b', r'\bUNION\b', r'\bEXEC\b', r'\bALTER\b']
        for pattern in dangerous_sql:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        # Remove null bytes
        text = text.replace('\x00', '')
        # Limit length
        return text.strip()[:max_length]

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format and check disposable domains"""
        if not email:
            return False, "Email required"
        
        # Basic format
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        if len(email) > 100:
            return False, "Email too long"
        
        # Check disposable domains
        email_lower = email.lower().strip()
        domain = email_lower.split('@')[1] if '@' in email_lower else ''
        if domain in SecurityValidator.DISPOSABLE_DOMAINS:
            return False, "Disposable emails not allowed"
        
        return True, email_lower

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number format"""
        if not phone:
            return False, "Phone required"
        
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        if not phone.startswith('+'):
            phone = '+' + phone
        
        if not re.match(r'^\+\d{7,15}$', phone):
            return False, "Invalid phone number"
        
        return True, phone

    @staticmethod
    def validate_amount(amount) -> Tuple[bool, str]:
        """Validate transaction amount"""
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return False, "Invalid amount"
        
        if amount <= 0:
            return False, "Amount must be positive"
        if amount > 10000000:  # 1 crore
            return False, "Amount exceeds maximum (₹1,00,00,000)"
        
        return True, round(amount, 2)

    @staticmethod
    def detect_bot(user_agent: str = "", ip: str = "") -> bool:
        """Detect common bot and scraper patterns"""
        if not user_agent:
            return True  # No UA = suspicious
        
        ua_lower = user_agent.lower()
        
        # Known bot patterns
        bot_patterns = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
            'python-requests', 'python-urllib', 'go-http-client', 'java/',
            'libwww', 'httpclient', 'nutch', 'phpcrawl', 'msnbot',
            'slurp', 'yandexbot', 'baiduspider', 'facebookexternalhit'
        ]
        
        for pattern in bot_patterns:
            if pattern in ua_lower:
                return True
        
        # Empty or very short UA
        if len(user_agent) < 20:
            return True
        
        return False

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if len(password) > 128:
            return False, "Password too long"
        if not re.search(r'[A-Z]', password):
            return False, "Password needs an uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password needs a lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password needs a number"
        return True, "Password is strong"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize file upload names"""
        filename = re.sub(r'[^\w\.\-]', '_', filename)
        filename = re.sub(r'\.{2,}', '.', filename)
        return filename[:100]

security = SecurityValidator()