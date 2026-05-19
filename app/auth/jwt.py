from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings
from app.schemas.auth import TokenData


def create_access_token(email: str, role: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": email, "role": role, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload["sub"]
        role: str = payload["role"]
        return TokenData(email=email, role=role)
    except (JWTError, KeyError) as exc:
        raise ValueError("Invalid or expired token") from exc
