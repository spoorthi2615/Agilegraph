from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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
        print("AUTH ERROR: No credentials provided (missing Authorization header)")
        return None

    token = credentials.credentials

    if not settings.SUPABASE_JWT_SECRET:
        print("AUTH ERROR: SUPABASE_JWT_SECRET is empty in environment variables!")
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )

        user_id = payload.get("sub")
        email = payload.get("email", "")

        if not user_id:
            print("AUTH ERROR: JWT decoded successfully, but 'sub' (user_id) is missing.")
            return None

        admin_emails = [e.strip().lower() for e in settings.ADMIN_EMAILS.split(",") if e.strip()]
        is_admin = email.lower() in admin_emails

        return User(user_id=user_id, email=email, is_admin=is_admin)

    except jwt.ExpiredSignatureError:
        print("AUTH ERROR: Token has expired!")
        return None
    except jwt.InvalidAudienceError:
        print("AUTH ERROR: Invalid audience (expected 'authenticated')")
        return None
    except jwt.PyJWTError as e:
        print(f"AUTH ERROR: Failed to decode JWT. Secret might be wrong. Error: {e}")
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
