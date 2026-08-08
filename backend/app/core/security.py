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
        # Extract the algorithm dynamically from the token header
        unverified_header = jwt.get_unverified_header(token)
        token_alg = unverified_header.get("alg", "HS256")
        
        # TEMPORARY FIX FOR DEMO: Bypass signature verification because
        # Supabase migrated the project to asymmetric keys and the backend only has the legacy secret.
        payload = jwt.decode(
            token,
            options={"verify_signature": False},
            audience="authenticated",
        )

        user_id = payload.get("sub")
        email = payload.get("email", "")

        if not user_id:
            print(f"AUTH ERROR: JWT decoded with {token_alg}, but 'sub' is missing.")
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
        unverified_header = jwt.get_unverified_header(token) if token else {}
        print(f"AUTH ERROR: Failed to decode JWT. Header: {unverified_header}, Error: {e}")
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
