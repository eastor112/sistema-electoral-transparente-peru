from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt

from election_system.application.ports import (
    AuthRepositoryPort,
    EmailSenderPort,
    TelegramSenderPort,
)
from election_system.core.config import settings
from election_system.core.exceptions import (
    ChallengeInvalidError,
    ConflictError,
    DeliveryChannelUnavailableError,
    InvalidCredentialsError,
)
from election_system.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp_code,
    hash_otp_code,
    hash_password,
    verify_password,
)
from election_system.domain.models import AuthUser, EmailOTPChallenge, OTPPurpose


@dataclass(frozen=True)
class LoginChallengeResult:
    challenge_id: str
    expires_at: datetime
    channel: Literal["email", "telegram"]


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    def __init__(
        self,
        *,
        repository: AuthRepositoryPort,
        email_sender: EmailSenderPort,
        telegram_sender: TelegramSenderPort,
    ) -> None:
        self._repository = repository
        self._email_sender = email_sender
        self._telegram_sender = telegram_sender

    async def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None,
        telegram_chat_id: str | None,
    ) -> AuthUser:
        existing = await self._repository.get_user_by_email(email)
        if existing is not None:
            raise ConflictError("Email already registered")

        password_hashed = hash_password(password)
        return await self._repository.create_user(
            email=email,
            password_hash=password_hashed,
            full_name=full_name,
            telegram_chat_id=telegram_chat_id,
        )

    async def start_login(
        self,
        *,
        email: str,
        password: str,
        channel: Literal["email", "telegram"] = "email",
    ) -> LoginChallengeResult:
        user = await self._repository.get_user_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        # Validate channel availability BEFORE mutating any state.
        if channel == "telegram" and user.telegram_chat_id is None:
            raise DeliveryChannelUnavailableError("User does not have Telegram configured")

        await self._repository.invalidate_user_challenges(user_id=user.user_id, purpose=OTPPurpose.LOGIN)
        challenge, code = await self._create_email_challenge(user_id=user.user_id, purpose=OTPPurpose.LOGIN)

        if channel == "telegram":
            await self._telegram_sender.send_message(
                chat_id=user.telegram_chat_id,  # type: ignore[arg-type]  # checked above
                text=(
                    "Election System: tu codigo de acceso es "
                    f"{code}. Vence en {settings.otp_ttl_minutes} minutos."
                ),
            )
        else:
            await self._email_sender.send_email(
                to_email=user.email,
                subject="Codigo de acceso Election System",
                text_body=(
                    "Tu codigo de acceso es: "
                    f"{code}. Este codigo vence en {settings.otp_ttl_minutes} minutos."
                ),
                html_body=None,
            )

        return LoginChallengeResult(
            challenge_id=challenge.challenge_id,
            expires_at=challenge.expires_at,
            channel=channel,
        )

    async def verify_login_code(self, *, challenge_id: str, code: str) -> TokenPair:
        challenge = await self._repository.get_challenge(challenge_id)
        challenge = self._assert_valid_challenge(challenge=challenge, expected_purpose=OTPPurpose.LOGIN)

        if challenge.code_hash != hash_otp_code(code):
            await self._repository.increment_challenge_attempt(challenge_id)
            raise ChallengeInvalidError("Invalid challenge code")

        await self._repository.consume_challenge(challenge_id)
        await self._repository.touch_last_login(user_id=challenge.user_id)
        return self._create_token_pair(subject=challenge.user_id)

    async def refresh(self, *, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except jwt.InvalidTokenError as exc:
            raise InvalidCredentialsError("Invalid refresh token") from exc

        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise InvalidCredentialsError("Invalid refresh token")

        user = await self._repository.get_user_by_id(subject)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid refresh token")

        return self._create_token_pair(subject=user.user_id)

    async def request_password_reset(self, *, email: str) -> None:
        user = await self._repository.get_user_by_email(email)
        if user is None or not user.is_active:
            return

        await self._repository.invalidate_user_challenges(
            user_id=user.user_id,
            purpose=OTPPurpose.PASSWORD_RESET,
        )
        challenge, code = await self._create_email_challenge(
            user_id=user.user_id,
            purpose=OTPPurpose.PASSWORD_RESET,
        )

        await self._email_sender.send_email(
            to_email=user.email,
            subject="Codigo de recuperacion Election System",
            text_body=(
                "Tu codigo para recuperar la cuenta es: "
                f"{code}. Challenge ID: {challenge.challenge_id}."
            ),
            html_body=None,
        )

    async def confirm_password_reset(
        self,
        *,
        email: str,
        challenge_id: str,
        code: str,
        new_password: str,
    ) -> None:
        user = await self._repository.get_user_by_email(email)
        if user is None or not user.is_active:
            raise ChallengeInvalidError("Invalid reset challenge")

        challenge = await self._repository.get_challenge(challenge_id)
        challenge = self._assert_valid_challenge(
            challenge=challenge,
            expected_purpose=OTPPurpose.PASSWORD_RESET,
        )
        if challenge.user_id != user.user_id:
            raise ChallengeInvalidError("Invalid reset challenge")

        if challenge.code_hash != hash_otp_code(code):
            await self._repository.increment_challenge_attempt(challenge_id)
            raise ChallengeInvalidError("Invalid reset challenge")

        await self._repository.consume_challenge(challenge_id)
        await self._repository.invalidate_user_challenges(
            user_id=user.user_id,
            purpose=OTPPurpose.PASSWORD_RESET,
        )
        await self._repository.update_user_password(
            user_id=user.user_id,
            password_hash=hash_password(new_password),
        )

    async def me(self, *, user_id: str) -> AuthUser:
        user = await self._repository.get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid user")
        return user

    async def register_telegram_chat_id(self, *, user_id: str, telegram_chat_id: str) -> None:
        user = await self._repository.get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid user")

        existing = await self._repository.get_user_by_telegram_chat_id(telegram_chat_id)
        if existing is not None and existing.user_id != user_id:
            raise ConflictError("Telegram chat id already in use")

        try:
            await self._telegram_sender.send_message(
                chat_id=telegram_chat_id,
                text="Election System: tu cuenta fue vinculada correctamente a este chat.",
            )
        except Exception as exc:
            raise DeliveryChannelUnavailableError(
                "No fue posible enviar mensaje al chat de Telegram"
            ) from exc

        await self._repository.update_user_telegram_chat_id(
            user_id=user_id,
            telegram_chat_id=telegram_chat_id,
        )

    async def _create_email_challenge(
        self,
        *,
        user_id: str,
        purpose: OTPPurpose,
    ) -> tuple[EmailOTPChallenge, str]:
        code = generate_otp_code()
        expires_at = datetime.now(UTC) + timedelta(minutes=settings.otp_ttl_minutes)
        challenge = await self._repository.create_otp_challenge(
            user_id=user_id,
            purpose=purpose,
            code_hash=hash_otp_code(code),
            expires_at=expires_at,
            max_attempts=settings.otp_max_attempts,
        )
        return challenge, code

    @staticmethod
    def _assert_valid_challenge(
        *, challenge: EmailOTPChallenge | None, expected_purpose: OTPPurpose
    ) -> EmailOTPChallenge:
        if challenge is None:
            raise ChallengeInvalidError("Challenge not found")

        if challenge.purpose != expected_purpose:
            raise ChallengeInvalidError("Challenge type mismatch")
        if challenge.consumed_at is not None:
            raise ChallengeInvalidError("Challenge already consumed")
        if challenge.attempts >= challenge.max_attempts:
            raise ChallengeInvalidError("Challenge attempts exceeded")
        if challenge.expires_at <= datetime.now(UTC):
            raise ChallengeInvalidError("Challenge expired")
        return challenge

    @staticmethod
    def _create_token_pair(*, subject: str) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(subject=subject),
            refresh_token=create_refresh_token(subject=subject),
        )
