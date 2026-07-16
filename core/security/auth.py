from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings

security = HTTPBearer()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_login_token(user_id: str, email: str, mode: str, phone: str, name: str) -> str:
    """Create token with mode (customer/provider)"""
    return create_access_token({
        "sub": user_id,
        "email": email,
        "mode": mode,          # "customer" or "provider"
        "phone": phone,
        "name": name
    })

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "mode": payload.get("mode", "customer"),
        "phone": payload.get("phone", ""),
        "name": payload.get("name", "User")
    }

def create_switch_token(old_payload: dict, new_mode: str) -> str:
    """Create new token when switching mode"""
    return create_login_token(
        user_id=old_payload.get("sub"),
        email=old_payload.get("email"),
        mode=new_mode,
        phone=old_payload.get("phone", ""),
        name=old_payload.get("name", "User")
    )