import logging
from config.settings import settings

logger = logging.getLogger("dokets.whatsapp")

class WhatsAppBot:
    def __init__(self):
        self.from_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', '+14155238886')
        self.client = None
        logger.info("WhatsApp bot ready (simulation mode)")

    def send_message(self, to_number, message):
        logger.info(f"[WHATSAPP] To: {to_number} | {message[:50]}...")
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