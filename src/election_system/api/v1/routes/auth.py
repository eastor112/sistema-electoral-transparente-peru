from datetime import datetime
from typing import Annotated, Literal, NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.api.dependencies.auth import CurrentActor, get_current_actor
from election_system.application.services.auth_service import (
    AuthService,
    LoginChallengeResult,
    TokenPair,
)
from election_system.core.exceptions import (
    ChallengeInvalidError,
    ConflictError,
    DeliveryChannelUnavailableError,
    InvalidCredentialsError,
)
from election_system.infrastructure.db.session import get_db_session
from election_system.infrastructure.notifications.email_sender import build_email_sender
from election_system.infrastructure.notifications.telegram_sender import build_telegram_sender
from election_system.infrastructure.repositories.auth_repository import AuthRepository

router = APIRouter(prefix="/auth")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=120)
    telegram_chat_id: str | None = Field(default=None, min_length=3, max_length=64)


class RegisterResponse(BaseModel):
    user_id: str
    email: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    channel: Literal["email", "telegram"] = "email"


class LoginChallengeResponse(BaseModel):
    challenge_id: str
    expires_at: datetime
    channel: Literal["email", "telegram"]
    message: str


class VerifyLoginCodeRequest(BaseModel):
    challenge_id: str = Field(min_length=36, max_length=36)
    code: str = Field(min_length=4, max_length=12)


class RegisterTelegramChatIdRequest(BaseModel):
    telegram_chat_id: str = Field(min_length=3, max_length=64)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class PasswordRecoveryRequest(BaseModel):
    email: EmailStr


class PasswordRecoveryConfirmRequest(BaseModel):
    email: EmailStr
    challenge_id: str = Field(min_length=36, max_length=36)
    code: str = Field(min_length=4, max_length=12)
    new_password: str = Field(min_length=8, max_length=128)


class MeResponse(BaseModel):
    user_id: str
    email: str
    full_name: str | None
    telegram_chat_id: str | None


class RegisterTelegramChatIdResponse(BaseModel):
    message: str
    telegram_chat_id: str


def _get_auth_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthService:
    return AuthService(
        repository=AuthRepository(db_session),
        email_sender=build_email_sender(),
        telegram_sender=build_telegram_sender(),
    )


def _raise_auth_http_error(exc: Exception) -> NoReturn:
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if isinstance(exc, InvalidCredentialsError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    if isinstance(exc, ChallengeInvalidError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if isinstance(exc, DeliveryChannelUnavailableError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    raise exc


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> RegisterResponse:
    try:
        user = await service.register(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            telegram_chat_id=payload.telegram_chat_id,
        )
    except Exception as exc:
        _raise_auth_http_error(exc)

    return RegisterResponse(user_id=user.user_id, email=user.email)


@router.post("/login", response_model=LoginChallengeResponse)
async def login(
    payload: LoginRequest,
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> LoginChallengeResponse:
    try:
        challenge: LoginChallengeResult = await service.start_login(
            email=payload.email,
            password=payload.password,
            channel=payload.channel,
        )
    except Exception as exc:
        _raise_auth_http_error(exc)

    return LoginChallengeResponse(
        challenge_id=challenge.challenge_id,
        expires_at=challenge.expires_at,
        channel=challenge.channel,
        message=f"Codigo enviado por {challenge.channel}",
    )


@router.post("/login/verify", response_model=TokenPair)
async def verify_login(
    payload: VerifyLoginCodeRequest,
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> TokenPair:
    try:
        return await service.verify_login_code(
            challenge_id=payload.challenge_id,
            code=payload.code,
        )
    except Exception as exc:
        _raise_auth_http_error(exc)


@router.post("/telegram/register-chat-id", response_model=RegisterTelegramChatIdResponse)
async def register_telegram_chat_id(
    payload: RegisterTelegramChatIdRequest,
    actor: Annotated[CurrentActor, Depends(get_current_actor)],
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> RegisterTelegramChatIdResponse:
    try:
        await service.register_telegram_chat_id(
            user_id=actor.actor_id,
            telegram_chat_id=payload.telegram_chat_id,
        )
    except Exception as exc:
        _raise_auth_http_error(exc)

    return RegisterTelegramChatIdResponse(
        message="Chat de Telegram registrado correctamente.",
        telegram_chat_id=payload.telegram_chat_id,
    )


@router.post("/password-recovery/request")
async def request_password_recovery(
    payload: PasswordRecoveryRequest,
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> dict[str, str]:
    await service.request_password_reset(email=payload.email)
    return {"message": "Si la cuenta existe, se envio un codigo al correo."}


@router.post("/password-recovery/confirm")
async def confirm_password_recovery(
    payload: PasswordRecoveryConfirmRequest,
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> dict[str, str]:
    try:
        await service.confirm_password_reset(
            email=payload.email,
            challenge_id=payload.challenge_id,
            code=payload.code,
            new_password=payload.new_password,
        )
    except Exception as exc:
        _raise_auth_http_error(exc)
    return {"message": "Contrasena actualizada correctamente."}


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    payload: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> TokenPair:
    try:
        return await service.refresh(refresh_token=payload.refresh_token)
    except Exception as exc:
        _raise_auth_http_error(exc)


@router.get("/me", response_model=MeResponse)
async def me(
    actor: Annotated[CurrentActor, Depends(get_current_actor)],
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> MeResponse:
    try:
        user = await service.me(user_id=actor.actor_id)
    except Exception as exc:
        _raise_auth_http_error(exc)
    return MeResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        telegram_chat_id=user.telegram_chat_id,
    )
