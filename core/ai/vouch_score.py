"""
Dokets VouchAI - Vouch Score Engine
"""

class VouchScoreEngine:
    def calculate_score(self, total_contracts: int, completed: int, disputed: int, on_time: int) -> float:
        if total_contracts == 0:
            return 100.0
        
        completion_rate = completed / total_contracts
        dispute_rate = 1 - (disputed / total_contracts)
        on_time_rate = on_time / max(completed, 1)
        
        score = (completion_rate * 40 + dispute_rate * 35 + on_time_rate * 25)
        return round(min(score, 100), 1)
    
    def get_level(self, score: float) -> str:
        if score >= 95: return "Diamond"
        if score >= 90: return "Platinum"
        if score >= 80: return "Gold"
        if score >= 70: return "Silver"
        if score >= 50: return "Bronze"
        return "New"

vouch_engine = VouchScoreEngine()