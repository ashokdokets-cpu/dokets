import logging
from datetime import datetime

logger = logging.getLogger("dokets.notifications")

class NotificationSystem:
    def __init__(self):
        self.notifications = []

    def send(self, user_id, title, message, type="info"):
        notif = {
            "id": f"NOTIF-{len(self.notifications)+1:04d}",
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type,
            "is_read": False,
            "created_at": str(datetime.utcnow())
        }
        self.notifications.append(notif)
        logger.info(f"Notification: {title}")
        return notif

    def get_user_notifications(self, user_id, unread_only=False):
        notifs = [n for n in self.notifications if n["user_id"] == user_id]
        if unread_only:
            notifs = [n for n in notifs if not n["is_read"]]
        return sorted(notifs, key=lambda x: x["created_at"], reverse=True)

    def mark_read(self, notif_id):
        for n in self.notifications:
            if n["id"] == notif_id:
                n["is_read"] = True
                return True
        return False

    def send_payment_received(self, user_id, amount, currency):
        self.send(user_id, "Payment", f"Received {currency} {amount}", "success")

notifications = NotificationSystem()