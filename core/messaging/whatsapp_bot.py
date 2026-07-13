import logging
import os
from config.settings import settings

logger = logging.getLogger("dokets.whatsapp")

class WhatsAppBot:
    def __init__(self):
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.client = None
        
        if self.account_sid and self.auth_token and self.auth_token != "demo_token":
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("WhatsApp LIVE - real messages!")
            except Exception as e:
                logger.warning(f"WhatsApp init error: {e}")
        else:
            logger.info("WhatsApp simulation mode - no valid token")

    def send_message(self, to_number, message):
        if self.client:
            try:
                msg = self.client.messages.create(
                    body=message,
                    from_=f"whatsapp:{self.from_number}",
                    to=f"whatsapp:{to_number}"
                )
                return {"success": True, "sent": True, "sid": msg.sid}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": True, "simulated": True, "message": message}

    def process_incoming(self, from_number, message):
        message = message.strip().upper()
        if message.startswith("NEW"):
            return {"action": "create_contract", "message": message[3:].strip(), "from": from_number}
        elif message.startswith("ACCEPT"):
            return {"action": "approve_contract", "contract_id": message[6:].strip(), "from": from_number}
        elif message == "HELP":
            return {"action": "help", "from": from_number}
        return {"action": "unknown", "from": from_number}

    def get_help_message(self):
        return "Dokets VouchAI Bot\nCommands: NEW [desc], ACCEPT [id], HELP"

whatsapp_bot = WhatsAppBot()