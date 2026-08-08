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


# Initialize PyJWKClient globally to take advantage of its internal caching
# This prevents fetching the JWKS on every single API request, which avoids rate limiting
jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
jwks_client = jwt.PyJWKClient(jwks_url)


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
        
        # Verify the signature properly
        if token_alg == "HS256":
            # Legacy symmetric signature
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=[token_alg],
                audience="authenticated",
            )
        else:
            try:
                signing_key = jwks_client.get_signing_key_from_jwt(token).key
            except jwt.exceptions.PyJWKClientError:
                # If 'kid' is missing from the token header, fallback to the first key in the JWKS
                keys = jwks_client.get_signing_keys()
                if not keys:
                    print("AUTH ERROR: No keys found in Supabase JWKS endpoint")
                    return None
                signing_key = keys[0].key
            
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=[token_alg],
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
