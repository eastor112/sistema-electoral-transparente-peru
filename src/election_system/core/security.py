from datetime import UTC, datetime, timedelta

from election_system.core.config import settings


def create_access_token(subject: str) -> str:
    # TODO: Replace with signed JWT implementation.
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return f"TODO_TOKEN::{subject}::{int(expires_at.timestamp())}"
