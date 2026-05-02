from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class MesaEstado(StrEnum):
    CONFIGURADA = "CONFIGURADA"
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"


# ---------------------------------------------------------------------------
# Roles y permisos (RBAC + ABAC)
# ---------------------------------------------------------------------------


class RoleType(StrEnum):
    """Roles del sistema electoral según plan 09."""

    ADMIN_NACIONAL = "ADMIN_NACIONAL"
    """Administración nacional: configura catálogos globales y políticas."""

    ADMIN_REGIONAL = "ADMIN_REGIONAL"
    """Administración regional/local: opera dentro de su ámbito de ubigeo."""

    MIEMBRO_MESA_TITULAR = "MIEMBRO_MESA_TITULAR"
    """Presidente, secretario o tercer miembro de una mesa."""

    MIEMBRO_MESA_SUPLENTE = "MIEMBRO_MESA_SUPLENTE"
    """Suplente: opera solo cuando el sistema registra su activación."""

    ELECTOR_AD_HOC = "ELECTOR_AD_HOC"
    """Elector designado excepcionalmente para completar mesa."""

    FISCALIZADOR = "FISCALIZADOR"
    """Fiscalizador ONPE/JNE: acceso de observación y validación."""

    PERSONERO = "PERSONERO"
    """Personero de partido: observación + reporte de incidencias."""

    ELECTOR = "ELECTOR"
    """Elector ciudadano: acceso de solo lectura a datos públicos."""


class Permission(StrEnum):
    """Permisos granulares del sistema."""

    # Mesas
    MESA_READ = "MESA_READ"
    MESA_WRITE = "MESA_WRITE"
    MESA_ASSIGN = "MESA_ASSIGN"

    # Actores / usuarios
    ACTOR_READ = "ACTOR_READ"
    ACTOR_WRITE = "ACTOR_WRITE"
    ACTOR_ASSIGN_ROLE = "ACTOR_ASSIGN_ROLE"

    # Actas
    ACTA_READ = "ACTA_READ"
    ACTA_WRITE = "ACTA_WRITE"
    ACTA_SIGN = "ACTA_SIGN"

    # Cédula electoral
    CEDULA_READ = "CEDULA_READ"
    CEDULA_WRITE = "CEDULA_WRITE"
    CEDULA_FREEZE = "CEDULA_FREEZE"

    # Jornada
    JORNADA_OPEN = "JORNADA_OPEN"
    JORNADA_CLOSE = "JORNADA_CLOSE"

    # Incidencias
    INCIDENCIA_READ = "INCIDENCIA_READ"
    INCIDENCIA_WRITE = "INCIDENCIA_WRITE"

    # Panel / catálogos
    ADMIN_PANEL = "ADMIN_PANEL"

    # Lectura pública ciudadana
    PUBLIC_READ = "PUBLIC_READ"


_ALL_PERMISSIONS: frozenset[Permission] = frozenset(Permission)

# Permisos por rol (RBAC base; ABAC restringe adicionalmente por scope)
ROLE_PERMISSIONS: dict[RoleType, frozenset[Permission]] = {
    RoleType.ADMIN_NACIONAL: _ALL_PERMISSIONS,
    RoleType.ADMIN_REGIONAL: frozenset(
        {
            Permission.MESA_READ,
            Permission.MESA_WRITE,
            Permission.MESA_ASSIGN,
            Permission.ACTOR_READ,
            Permission.ACTOR_WRITE,
            Permission.ACTA_READ,
            Permission.CEDULA_READ,
            Permission.INCIDENCIA_READ,
            Permission.ADMIN_PANEL,
            Permission.PUBLIC_READ,
        }
    ),
    RoleType.MIEMBRO_MESA_TITULAR: frozenset(
        {
            Permission.MESA_READ,
            Permission.ACTA_READ,
            Permission.ACTA_WRITE,
            Permission.ACTA_SIGN,
            Permission.CEDULA_READ,
            Permission.INCIDENCIA_READ,
            Permission.INCIDENCIA_WRITE,
            Permission.JORNADA_OPEN,
            Permission.JORNADA_CLOSE,
            Permission.PUBLIC_READ,
        }
    ),
    RoleType.MIEMBRO_MESA_SUPLENTE: frozenset(
        {
            Permission.MESA_READ,
            Permission.ACTA_READ,
            Permission.ACTA_WRITE,
            Permission.ACTA_SIGN,
            Permission.CEDULA_READ,
            Permission.INCIDENCIA_READ,
            Permission.INCIDENCIA_WRITE,
            Permission.JORNADA_OPEN,
            Permission.JORNADA_CLOSE,
            Permission.PUBLIC_READ,
        }
    ),
    RoleType.ELECTOR_AD_HOC: frozenset(
        {
            Permission.MESA_READ,
            Permission.ACTA_READ,
            Permission.ACTA_WRITE,
            Permission.ACTA_SIGN,
            Permission.CEDULA_READ,
            Permission.INCIDENCIA_READ,
            Permission.INCIDENCIA_WRITE,
            Permission.JORNADA_OPEN,
            Permission.JORNADA_CLOSE,
            Permission.PUBLIC_READ,
        }
    ),
    RoleType.FISCALIZADOR: frozenset(
        {
            Permission.MESA_READ,
            Permission.ACTA_READ,
            Permission.ACTA_SIGN,
            Permission.CEDULA_READ,
            Permission.INCIDENCIA_READ,
            Permission.PUBLIC_READ,
        }
    ),
    RoleType.PERSONERO: frozenset(
        {
            Permission.MESA_READ,
            Permission.ACTA_READ,
            Permission.ACTA_SIGN,
            Permission.CEDULA_READ,
            Permission.INCIDENCIA_READ,
            Permission.INCIDENCIA_WRITE,
            Permission.PUBLIC_READ,
        }
    ),
    RoleType.ELECTOR: frozenset(
        {
            Permission.INCIDENCIA_READ,
            Permission.PUBLIC_READ,
        }
    ),
}


@dataclass(frozen=True)
class UserRole:
    """Asignación de rol a un usuario con ámbito opcional (ABAC)."""

    user_role_id: str
    user_id: str
    role_type: RoleType
    # Atributos de ámbito (ABAC) — None = ámbito global
    mesa_id: str | None
    ubigeo: str | None
    jornada_id: str | None
    is_active: bool
    assigned_by: str
    assigned_at: datetime
    revoked_at: datetime | None

    @property
    def permissions(self) -> frozenset[Permission]:
        return ROLE_PERMISSIONS[self.role_type]

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions


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
