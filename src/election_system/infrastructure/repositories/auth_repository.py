from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.domain.models import AuthUser, EmailOTPChallenge, OTPPurpose
from election_system.infrastructure.db.models import EmailOTPChallengeORM, UserORM


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user_by_email(self, email: str) -> AuthUser | None:
        stmt: Select[tuple[UserORM]] = select(UserORM).where(UserORM.email == email.lower())
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return _map_user(user)

    async def get_user_by_id(self, user_id: str) -> AuthUser | None:
        stmt: Select[tuple[UserORM]] = select(UserORM).where(UserORM.user_id == user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return _map_user(user)

    async def get_user_by_telegram_chat_id(self, telegram_chat_id: str) -> AuthUser | None:
        stmt: Select[tuple[UserORM]] = select(UserORM).where(
            UserORM.telegram_chat_id == telegram_chat_id
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return _map_user(user)

    async def create_user(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str | None,
        telegram_chat_id: str | None,
    ) -> AuthUser:
        user = UserORM(
            user_id=str(uuid4()),
            email=email.lower(),
            full_name=full_name,
            telegram_chat_id=telegram_chat_id,
            password_hash=password_hash,
            is_active=True,
        )
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return _map_user(user)

    async def update_user_password(self, *, user_id: str, password_hash: str) -> None:
        stmt = (
            update(UserORM)
            .where(UserORM.user_id == user_id)
            .values(password_hash=password_hash, updated_at=datetime.now(UTC))
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def update_user_telegram_chat_id(self, *, user_id: str, telegram_chat_id: str) -> None:
        stmt = (
            update(UserORM)
            .where(UserORM.user_id == user_id)
            .values(telegram_chat_id=telegram_chat_id, updated_at=datetime.now(UTC))
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def touch_last_login(self, *, user_id: str) -> None:
        stmt = (
            update(UserORM)
            .where(UserORM.user_id == user_id)
            .values(last_login_at=datetime.now(UTC), updated_at=datetime.now(UTC))
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def create_otp_challenge(
        self,
        *,
        user_id: str,
        purpose: OTPPurpose,
        code_hash: str,
        expires_at: datetime,
        max_attempts: int,
    ) -> EmailOTPChallenge:
        challenge = EmailOTPChallengeORM(
            challenge_id=str(uuid4()),
            user_id=user_id,
            purpose=purpose.value,
            code_hash=code_hash,
            attempts=0,
            max_attempts=max_attempts,
            expires_at=expires_at,
        )
        self._session.add(challenge)
        await self._session.commit()
        await self._session.refresh(challenge)
        return _map_challenge(challenge)

    async def get_challenge(self, challenge_id: str) -> EmailOTPChallenge | None:
        stmt: Select[tuple[EmailOTPChallengeORM]] = select(EmailOTPChallengeORM).where(
            EmailOTPChallengeORM.challenge_id == challenge_id
        )
        result = await self._session.execute(stmt)
        challenge = result.scalar_one_or_none()
        if challenge is None:
            return None
        return _map_challenge(challenge)

    async def increment_challenge_attempt(self, challenge_id: str) -> None:
        stmt = (
            update(EmailOTPChallengeORM)
            .where(EmailOTPChallengeORM.challenge_id == challenge_id)
            .values(attempts=EmailOTPChallengeORM.attempts + 1)
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def consume_challenge(self, challenge_id: str) -> None:
        stmt = (
            update(EmailOTPChallengeORM)
            .where(EmailOTPChallengeORM.challenge_id == challenge_id)
            .values(consumed_at=datetime.now(UTC))
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def invalidate_user_challenges(self, *, user_id: str, purpose: OTPPurpose) -> None:
        stmt = (
            update(EmailOTPChallengeORM)
            .where(
                EmailOTPChallengeORM.user_id == user_id,
                EmailOTPChallengeORM.purpose == purpose.value,
                EmailOTPChallengeORM.consumed_at.is_(None),
            )
            .values(consumed_at=datetime.now(UTC))
        )
        await self._session.execute(stmt)
        await self._session.commit()


def _map_user(user: UserORM) -> AuthUser:
    return AuthUser(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        telegram_chat_id=user.telegram_chat_id,
        password_hash=user.password_hash,
        is_active=user.is_active,
    )


def _map_challenge(challenge: EmailOTPChallengeORM) -> EmailOTPChallenge:
    return EmailOTPChallenge(
        challenge_id=challenge.challenge_id,
        user_id=challenge.user_id,
        purpose=OTPPurpose(challenge.purpose),
        code_hash=challenge.code_hash,
        attempts=challenge.attempts,
        max_attempts=challenge.max_attempts,
        expires_at=challenge.expires_at,
        consumed_at=challenge.consumed_at,
    )
