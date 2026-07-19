"""
Dokets VouchAI - Email Notifications
"""
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings

logger = logging.getLogger("dokets.email")

class EmailNotifier:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASS", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@dokets.com")
        self.enabled = bool(self.smtp_user and self.smtp_pass)

    def send_email(self, to_email: str, subject: str, body: str):
        if not self.enabled:
            logger.info(f"Email simulation: {subject} to {to_email}")
            return {"success": True, "simulated": True}

        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            
            return {"success": True, "sent": True}
        except Exception as e:
            logger.error(f"Email failed: {e}")
            return {"success": False, "error": str(e)}

    def contract_created(self, to_email: str, title: str, amount: str, link: str):
        return self.send_email(to_email, f"New Contract: {title}",
            f"<h2>New Contract Created</h2><p><b>{title}</b></p><p>Amount: {amount}</p><p><a href='{link}'>View Contract</a></p>")

    def contract_accepted(self, to_email: str, title: str):
        return self.send_email(to_email, f"Contract Accepted: {title}",
            f"<h2>Provider Accepted!</h2><p><b>{title}</b></p><p>Work can now begin.</p>")

    def milestone_completed(self, to_email: str, title: str, amount: str):
        return self.send_email(to_email, f"Payment Released: {title}",
            f"<h2>Milestone Completed</h2><p><b>{title}</b></p><p>Amount: {amount} released.</p>")

    def review_received(self, to_email: str, rating: int, review: str):
        stars = "⭐" * rating
        return self.send_email(to_email, f"New Review: {stars}",
            f"<h2>{stars}</h2><p>{review}</p>")

try:
    email_notifier = EmailNotifier()
except Exception as e:
    import logging
    logging.getLogger("dokets.email").warning(f"Email notifier init failed: {e}")
    email_notifier = None