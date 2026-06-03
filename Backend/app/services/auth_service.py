import base64
import hashlib
import logging
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings

log = logging.getLogger(__name__)


def _prehash(plain: str) -> bytes:
    """SHA-256 prehash → 32 raw bytes → 44-byte base64.

    bcrypt hard-limits input to 72 bytes.  SHA-256 condenses any-length
    password to a fixed 44-byte ASCII string, preserving full entropy.
    """
    digest = hashlib.sha256(plain.encode("utf-8")).digest()
    return base64.b64encode(digest)  # 44 bytes, safe for bcrypt


def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_prehash(plain), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_prehash(plain), hashed.encode("utf-8"))


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    """Return the subject (user_id) from a valid token, or raise JWTError."""
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    sub: str | None = payload.get("sub")
    if sub is None:
        raise JWTError("Token has no subject")
    return sub
