"""
Dokets VouchAI - Anti-Fraud Detection
"""
from datetime import datetime, timedelta

class FraudDetection:
    def __init__(self):
        self.transactions = []
        self.blocked_ips = set()
    
    def check_transaction(self, user_id: str, amount: float, ip: str) -> dict:
        """Check for suspicious patterns"""
        flags = []
        
        # Check for rapid transactions
        recent = [t for t in self.transactions 
                  if t["user_id"] == user_id 
                  and datetime.utcnow() - t["time"] < timedelta(minutes=5)]
        if len(recent) > 10:
            flags.append("rapid_transactions")
        
        # Check for unusual amounts
        if amount > 500000:
            flags.append("high_value")
        
        # Check blocked IPs
        if ip in self.blocked_ips:
            flags.append("blocked_ip")
        
        is_suspicious = len(flags) > 0
        
        self.transactions.append({
            "user_id": user_id,
            "amount": amount,
            "time": datetime.utcnow(),
            "ip": ip
        })
        
        return {
            "suspicious": is_suspicious,
            "flags": flags,
            "blocked": ip in self.blocked_ips
        }
    
    def block_ip(self, ip: str):
        self.blocked_ips.add(ip)
    
    def unblock_ip(self, ip: str):
        self.blocked_ips.discard(ip)

fraud_detection = FraudDetection()