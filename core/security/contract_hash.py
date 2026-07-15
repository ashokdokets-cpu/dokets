"""
Dokets VouchAI - Tamper-Proof Contract Hashing
"""
import hashlib
import json
from datetime import datetime

class ContractHash:
    @staticmethod
    def generate_hash(contract: dict) -> str:
        """Generate SHA-256 hash of contract for tamper detection"""
        # Remove dynamic fields before hashing
        contract_copy = {k: v for k, v in contract.items() 
                        if k not in ['updated_at', 'provider_view_url', 'share_url']}
        contract_str = json.dumps(contract_copy, sort_keys=True, default=str)
        return hashlib.sha256(contract_str.encode()).hexdigest()
    
    @staticmethod
    def verify_integrity(contract: dict, stored_hash: str) -> bool:
        """Verify contract hasn't been tampered with"""
        current_hash = ContractHash.generate_hash(contract)
        return current_hash == stored_hash
    
    @staticmethod
    def create_audit_trail(contract_id: str, action: str, user_id: str) -> dict:
        """Create audit trail entry"""
        return {
            "contract_id": contract_id,
            "action": action,
            "user_id": user_id,
            "timestamp": str(datetime.utcnow()),
            "ip_hash": hashlib.sha256(str(user_id).encode()).hexdigest()[:8]
        }

contract_hash = ContractHash()