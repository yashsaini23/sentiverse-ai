import datetime
from datetime import timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(data: dict, expires_hours: int = 24) -> str:
    if not settings.SECRET_KEY:
        raise RuntimeError("Configure SECRET_KEY in the environment before creating access tokens.")
    expires_at = datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=expires_hours)
    return jwt.encode({**data, "exp": expires_at}, settings.SECRET_KEY, algorithm="HS256")
