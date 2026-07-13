import asyncio 
import sys 
sys.path.insert(0, '.') 
from api.routes.users import _users 
from core.security.auth import hash_password 
 
user = { 
    "id": "1", 
    "email": "test@test.com", 
    "phone_number": "+91123", 
    "full_name": "Test", 
    "hashed_password": hash_password("pass12345"), 
    "user_role": "customer", 
    "vouch_score": 100.0, 
    "total_contracts": 0 
} 
_users.append(user) 
print("User added:", _users[0]["email"]) 
print("Password verified:", __import__('core.security.auth').verify_password("pass12345", _users[0]["hashed_password"])) 
