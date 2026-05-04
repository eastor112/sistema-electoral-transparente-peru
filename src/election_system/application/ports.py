from datetime import datetime
from typing import Protocol

from election_system.domain.models import (
    AuthUser,
    Candidato,
    EmailOTPChallenge,
    EstadoProceso,
    ListaElectoral,
    OTPPurpose,
    PartidoPolitico,
    ProcesoElectoral,
    RoleType,
    TipoCargo,
    UserRole,
)


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


class RoleRepositoryPort(Protocol):
    async def get_active_roles_for_user(self, user_id: str) -> list[UserRole]: ...

    async def get_role(self, user_role_id: str) -> UserRole | None: ...

    async def assign_role(
        self,
        *,
        user_id: str,
        role_type: RoleType,
        assigned_by: str,
        mesa_id: str | None,
        ubigeo: str | None,
        jornada_id: str | None,
    ) -> UserRole: ...

    async def revoke_role(self, *, user_role_id: str, revoked_at: datetime) -> None: ...

    async def list_roles(
        self,
        *,
        user_id: str | None,
        role_type: RoleType | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[UserRole]: ...


# ---------------------------------------------------------------------------
# Cédula Electoral ports
# ---------------------------------------------------------------------------


class StoragePort(Protocol):
    async def upload_image(
        self,
        *,
        folder: str,
        data: bytes,
        content_type: str,
        original_filename: str,
    ) -> str: ...


class PartidoRepositoryPort(Protocol):
    async def create(
        self, *, nombre: str, numero: int
    ) -> PartidoPolitico: ...

    async def get_by_id(self, partido_id: str) -> PartidoPolitico | None: ...

    async def list_all(self, *, only_active: bool) -> list[PartidoPolitico]: ...

    async def update_simbolo_url(self, *, partido_id: str, simbolo_url: str) -> None: ...


class ProcesoRepositoryPort(Protocol):
    async def create(
        self,
        *,
        nombre: str,
        fecha_jornada: str,
        tipos_cargo: list[TipoCargo],
    ) -> ProcesoElectoral: ...

    async def get_by_id(self, proceso_id: str) -> ProcesoElectoral | None: ...

    async def list_all(self) -> list[ProcesoElectoral]: ...

    async def update_estado(
        self, *, proceso_id: str, estado: EstadoProceso
    ) -> None: ...

    async def create_lista(
        self,
        *,
        proceso_id: str,
        partido_id: str,
        tipo_cargo: TipoCargo,
    ) -> ListaElectoral: ...

    async def get_lista(self, lista_id: str) -> ListaElectoral | None: ...

    async def list_listas(self, proceso_id: str) -> list[ListaElectoral]: ...

    async def add_candidato(
        self,
        *,
        lista_id: str,
        nombre_completo: str,
        orden: int,
        es_titular: bool,
    ) -> Candidato: ...

    async def get_candidato(self, candidato_id: str) -> Candidato | None: ...

    async def list_candidatos(self, lista_id: str) -> list[Candidato]: ...

    async def update_candidato_foto_url(
        self, *, candidato_id: str, foto_url: str
    ) -> None: ...
