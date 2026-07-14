import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings

logger = logging.getLogger("dokets.email")

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "contact@dokets.com")
        self.ready = bool(self.smtp_server and self.username and self.password)
        if self.ready:
            logger.info(f"Email service ready: {self.from_email}")
        else:
            logger.info("Email in simulation mode")

    def send_email(self, to_email, subject, body):
        if self.ready:
            try:
                msg = MIMEMultipart()
                msg["From"] = self.from_email
                msg["To"] = to_email
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "html"))

                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)
                
                logger.info(f"Email sent to {to_email}: {subject}")
                return {"success": True, "sent": True}
            except Exception as e:
                logger.error(f"Email failed: {e}")
                return {"success": False, "error": str(e)}
        
        logger.info(f"[SIM] Email to {to_email}: {subject}")
        return {"success": True, "simulated": True}

    def send_welcome(self, to_email, name):
        body = f"""
        <div style="font-family:Arial;max-width:600px;margin:0 auto;padding:20px;">
            <div style="background:#6366F1;color:white;padding:20px;border-radius:10px 10px 0 0;text-align:center;">
                <h1>Welcome to Dokets! 🛡️</h1>
            </div>
            <div style="background:#F8FAFC;padding:20px;border-radius:0 0 10px 10px;">
                <h2>Hi {name},</h2>
                <p>Welcome to the future of trust-based contracts!</p>
                <p>With Dokets VouchAI, you can:</p>
                <ul>
                    <li>🤖 Create AI-powered contracts in seconds</li>
                    <li>🔒 Secure payments with escrow</li>
                    <li>⭐ Build your Vouch Score</li>
                </ul>
                <a href="https://dokets.com/dashboard" style="display:inline-block;background:#6366F1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Go to Dashboard</a>
            </div>
        </div>
        """
        return self.send_email(to_email, f"Welcome to Dokets, {name}!", body)

    def send_contract_notification(self, to_email, contract_title, amount, currency):
        body = f"""
        <div style="font-family:Arial;max-width:600px;margin:0 auto;padding:20px;">
            <h2>📋 New Contract</h2>
            <p><strong>{contract_title}</strong></p>
            <p>Amount: {currency} {amount}</p>
            <a href="https://dokets.com/dashboard" style="color:#6366F1;">View on Dokets</a>
        </div>
        """
        return self.send_email(to_email, f"New Contract: {contract_title}", body)

email_service = EmailService()