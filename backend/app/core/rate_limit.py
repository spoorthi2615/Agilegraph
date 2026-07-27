import time
from typing import Dict, List
from fastapi import Request, HTTPException, status

# Simple in-memory rate limiter for a single worker.
# In a distributed production system, Redis should be used.
_RATE_LIMITS: Dict[str, List[float]] = {}
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 60 # 60 requests per minute

def check_rate_limit(request: Request):
    """
    Checks if the client IP has exceeded the rate limit.
    Raises an HTTPException if the limit is exceeded.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Exclude health and operational endpoints from rate limits
    path = request.url.path
    if path.startswith("/api/v1/health") or path.startswith("/api/v1/metrics"):
        return
        
    now = time.time()
    
    if client_ip not in _RATE_LIMITS:
        _RATE_LIMITS[client_ip] = []
        
    # Remove timestamps older than the window
    _RATE_LIMITS[client_ip] = [t for t in _RATE_LIMITS[client_ip] if now - t < _WINDOW_SECONDS]
    
    if len(_RATE_LIMITS[client_ip]) >= _MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
        
    _RATE_LIMITS[client_ip].append(now)
