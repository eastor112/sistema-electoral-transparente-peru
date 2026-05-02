from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class MesaEstado(StrEnum):
    CONFIGURADA = "CONFIGURADA"
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"


@dataclass(frozen=True)
class Mesa:
    mesa_id: str
    local_id: str
    ubigeo: str
    estado: MesaEstado


@dataclass(frozen=True)
class FiabilidadMesa:
    mesa_id: str
    score: int
    nivel: str


class OTPPurpose(StrEnum):
    LOGIN = "LOGIN"
    PASSWORD_RESET = "PASSWORD_RESET"


@dataclass(frozen=True)
class AuthUser:
    user_id: str
    email: str
    full_name: str | None
    telegram_chat_id: str | None
    password_hash: str
    is_active: bool


@dataclass(frozen=True)
class EmailOTPChallenge:
    challenge_id: str
    user_id: str
    purpose: OTPPurpose
    code_hash: str
    attempts: int
    max_attempts: int
    expires_at: datetime
    consumed_at: datetime | None
