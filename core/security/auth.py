from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings

security = HTTPBearer()

# Track login attempts (in-memory, use Redis in production)
_login_attempts = {}

def hash_password(password: str) -> str:
    """Hash password with bcrypt (12 rounds)"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with constant-time comparison"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with expiry"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_login_token(user_id: str, email: str, mode: str, phone: str, name: str) -> str:
    """Create token with mode context"""
    return create_access_token({
        "sub": user_id,
        "email": email,
        "mode": mode,
        "phone": phone,
        "name": name
    })

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from token"""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
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

def check_rate_limit(key: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
    """Check if key has exceeded rate limit"""
    now = datetime.utcnow()
    if key in _login_attempts:
        attempts = [t for t in _login_attempts[key] if now - t < timedelta(minutes=window_minutes)]
        _login_attempts[key] = attempts
        if len(attempts) >= max_attempts:
            return False
    else:
        _login_attempts[key] = []
    _login_attempts[key].append(now)
    return True

def get_client_ip(request: Request) -> str:
    """Get real client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"