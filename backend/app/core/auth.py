import datetime as dt
import os

import jwt
from passlib.context import CryptContext

# Configure JWT_SECRET_KEY in the environment; there is intentionally no insecure default.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _secret_key() -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret or len(secret) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be set to a random value of at least 32 characters.")
    return secret


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=24)
    return jwt.encode(payload, _secret_key(), algorithm="HS256")
