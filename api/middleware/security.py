"""
Dokets VouchAI - Security Middleware
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from core.security.validator import security as validator

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Bot detection
        user_agent = request.headers.get("User-Agent", "")
        client_ip = request.client.host if request.client else "unknown"
        
        if validator.detect_bot(user_agent, client_ip):
            # Allow health checks and docs
            if request.url.path not in ["/health", "/docs", "/openapi.json"]:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response