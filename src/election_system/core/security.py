import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, cast

import jwt

from election_system.core.config import settings

TokenType = Literal["access", "refresh"]


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _timestamp(dt: datetime) -> int:
    return int(dt.timestamp())


def _create_token(*, subject: str, token_type: TokenType, expires_minutes: int) -> str:
    issued_at = _now_utc()
    expires_at = issued_at + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": _timestamp(issued_at),
        "exp": _timestamp(expires_at),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        token_type="access",
        expires_minutes=settings.jwt_access_token_expire_minutes,
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_minutes=settings.jwt_refresh_token_expire_minutes,
    )


def decode_token(token: str, *, expected_type: TokenType | None = None) -> dict[str, Any]:
    payload = cast(
        dict[str, Any],
        jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]),
    )
    if expected_type is not None and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Unexpected token type")
    return payload


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        settings.password_hash_iterations,
    )
    digest_b64 = base64.b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${settings.password_hash_iterations}${salt}${digest_b64}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, rounds_raw, salt, digest_b64 = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        rounds = int(rounds_raw)
    except ValueError:
        return False

    # Reject hashes with suspiciously low or abusively high iteration counts.
    # Low counts weaken the KDF; high counts are a DoS vector.
    _min_rounds = 100_000
    _max_rounds = 2_000_000
    if not (_min_rounds <= rounds <= _max_rounds):
        return False

    computed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        rounds,
    )
    expected = base64.b64decode(digest_b64.encode("ascii"))
    return hmac.compare_digest(computed, expected)


def generate_otp_code() -> str:
    max_code = 10**settings.otp_code_length
    number = secrets.randbelow(max_code)
    return str(number).zfill(settings.otp_code_length)


def hash_otp_code(code: str) -> str:
    """Return a constant-length HMAC-SHA256 hex digest of the OTP code.

    Uses a dedicated otp_hmac_key (separate from jwt_secret_key) so that
    compromise of one secret does not affect the other.
    """
    return hmac.new(
        settings.otp_hmac_key.encode(),
        code.encode(),
        hashlib.sha256,
    ).hexdigest()
