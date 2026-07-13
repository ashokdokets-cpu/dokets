import logging
import uuid
from datetime import datetime
from config.settings import settings

logger = logging.getLogger("dokets.email")

class EmailService:
    def __init__(self):
        self.verification_tokens = {}
        logger.info("Email service ready")

    def send_verification(self, email: str) -> str:
        token = str(uuid.uuid4())
        self.verification_tokens[email] = {
            "token": token,
            "created_at": datetime.utcnow(),
            "verified": False
        }
        # In production, send real email via SendGrid/Resend
        logger.info(f"[SIMULATION] Verification email sent to {email}")
        logger.info(f"[SIMULATION] Verify link: https://dokets.com/verify?email={email}&token={token}")
        return token

    def verify_email(self, email: str, token: str) -> bool:
        record = self.verification_tokens.get(email)
        if record and record["token"] == token:
            record["verified"] = True
            return True
        return False

    def is_verified(self, email: str) -> bool:
        record = self.verification_tokens.get(email)
        return record["verified"] if record else False

email_service = EmailService()