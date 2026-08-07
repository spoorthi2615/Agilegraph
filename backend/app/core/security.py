from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.config.settings import settings

security = HTTPBearer(auto_error=False)


class User:
    def __init__(self, user_id: str, email: str, is_admin: bool):
        self.id = user_id
        self.email = email
        self.is_admin = is_admin


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    if not credentials:
        # If no auth token is provided, return None or raise Exception depending on strictness.
        # For now, to gracefully degrade, we return None and allow routes to handle it.
        return None

    token = credentials.credentials

    if not settings.SUPABASE_JWT_SECRET:
        # If secret isn't configured, fallback gracefully to anonymous
        return None

    try:
        payload = jwt.decode(
            token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated"
        )

        user_id = payload.get("sub")
        email = payload.get("email", "")

        if not user_id:
            return None

        admin_emails = [e.strip().lower() for e in settings.ADMIN_EMAILS.split(",") if e.strip()]
        is_admin = email.lower() in admin_emails

        return User(user_id=user_id, email=email, is_admin=is_admin)

    except jwt.PyJWTError:
        return None


def get_current_user_strict(user: Optional[User] = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_admin_user(user: User = Depends(get_current_user_strict)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin privileges",
        )
    return user
