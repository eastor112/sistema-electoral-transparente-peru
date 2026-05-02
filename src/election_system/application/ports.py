from datetime import datetime
from typing import Protocol

from election_system.domain.models import AuthUser, EmailOTPChallenge, OTPPurpose


class MesaRepositoryPort(Protocol):
    async def exists(self, mesa_id: str) -> bool: ...


class EmailSenderPort(Protocol):
    async def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None: ...


class TelegramSenderPort(Protocol):
    async def send_message(self, *, chat_id: str, text: str) -> None: ...


class AuthRepositoryPort(Protocol):
    async def get_user_by_email(self, email: str) -> AuthUser | None: ...

    async def get_user_by_id(self, user_id: str) -> AuthUser | None: ...

    async def get_user_by_telegram_chat_id(self, telegram_chat_id: str) -> AuthUser | None: ...

    async def create_user(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str | None,
        telegram_chat_id: str | None,
    ) -> AuthUser: ...

    async def update_user_password(self, *, user_id: str, password_hash: str) -> None: ...

    async def update_user_telegram_chat_id(self, *, user_id: str, telegram_chat_id: str) -> None: ...

    async def touch_last_login(self, *, user_id: str) -> None: ...

    async def create_otp_challenge(
        self,
        *,
        user_id: str,
        purpose: OTPPurpose,
        code_hash: str,
        expires_at: datetime,
        max_attempts: int,
    ) -> EmailOTPChallenge: ...

    async def get_challenge(self, challenge_id: str) -> EmailOTPChallenge | None: ...

    async def increment_challenge_attempt(self, challenge_id: str) -> None: ...

    async def consume_challenge(self, challenge_id: str) -> None: ...

    async def invalidate_user_challenges(self, *, user_id: str, purpose: OTPPurpose) -> None: ...
