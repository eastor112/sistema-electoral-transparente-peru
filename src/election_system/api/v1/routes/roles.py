from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.api.dependencies.auth import CurrentActor, require_roles
from election_system.application.services.role_service import (
    AssignRoleResult,
    RoleNotFoundError,
    RoleService,
)
from election_system.core.exceptions import ConflictError
from election_system.domain.models import ROLE_PERMISSIONS, Permission, RoleType, UserRole
from election_system.infrastructure.db.session import get_db_session
from election_system.infrastructure.repositories.role_repository import RoleRepository

router = APIRouter(prefix="/roles")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class AssignRoleRequest(BaseModel):
    user_id: str
    role_type: RoleType
    mesa_id: str | None = None
    ubigeo: str | None = None
    jornada_id: str | None = None


class UserRoleResponse(BaseModel):
    user_role_id: str
    user_id: str
    role_type: RoleType
    mesa_id: str | None
    ubigeo: str | None
    jornada_id: str | None
    is_active: bool
    assigned_by: str
    assigned_at: datetime
    revoked_at: datetime | None
    permissions: list[Permission]

    @classmethod
    def from_domain(cls, role: UserRole) -> "UserRoleResponse":
        return cls(
            user_role_id=role.user_role_id,
            user_id=role.user_id,
            role_type=role.role_type,
            mesa_id=role.mesa_id,
            ubigeo=role.ubigeo,
            jornada_id=role.jornada_id,
            is_active=role.is_active,
            assigned_by=role.assigned_by,
            assigned_at=role.assigned_at,
            revoked_at=role.revoked_at,
            permissions=sorted(role.permissions),
        )


class PermissionsResponse(BaseModel):
    role_type: RoleType
    permissions: list[Permission]


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------


def _get_role_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RoleService:
    return RoleService(repository=RoleRepository(db_session))


_AdminActor = Annotated[
    CurrentActor,
    Depends(require_roles(RoleType.ADMIN_NACIONAL)),
]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
async def assign_role(
    payload: AssignRoleRequest,
    actor: _AdminActor,
    service: Annotated[RoleService, Depends(_get_role_service)],
) -> UserRoleResponse:
    """Asigna un rol a un usuario. Solo ADMIN_NACIONAL."""
    try:
        result: AssignRoleResult = await service.assign_role(
            user_id=payload.user_id,
            role_type=payload.role_type,
            assigned_by=actor.actor_id,
            mesa_id=payload.mesa_id,
            ubigeo=payload.ubigeo,
            jornada_id=payload.jornada_id,
        )
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UserRoleResponse.from_domain(result.user_role)


@router.delete("/{user_role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_role(
    user_role_id: str,
    _actor: _AdminActor,
    service: Annotated[RoleService, Depends(_get_role_service)],
) -> None:
    """Revoca una asignación de rol activa. Solo ADMIN_NACIONAL."""
    try:
        await service.revoke_role(user_role_id=user_role_id)
    except RoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[UserRoleResponse])
async def list_roles(
    _actor: _AdminActor,
    service: Annotated[RoleService, Depends(_get_role_service)],
    user_id: Annotated[str | None, Query()] = None,
    role_type: Annotated[RoleType | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = True,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[UserRoleResponse]:
    """Lista asignaciones de roles. Solo ADMIN_NACIONAL."""
    roles = await service.list_roles(
        user_id=user_id,
        role_type=role_type,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return [UserRoleResponse.from_domain(r) for r in roles]


@router.get("/users/{user_id}", response_model=list[UserRoleResponse])
async def get_user_roles(
    user_id: str,
    _actor: _AdminActor,
    service: Annotated[RoleService, Depends(_get_role_service)],
) -> list[UserRoleResponse]:
    """Devuelve los roles activos de un usuario. Solo ADMIN_NACIONAL."""
    roles = await service.get_user_roles(user_id)
    return [UserRoleResponse.from_domain(r) for r in roles]


@router.get("/catalog/permissions", response_model=list[PermissionsResponse])
async def get_permissions_catalog(
    _actor: _AdminActor,
) -> list[PermissionsResponse]:
    """Devuelve el catálogo de permisos por tipo de rol."""
    return [
        PermissionsResponse(
            role_type=role_type,
            permissions=sorted(perms),
        )
        for role_type, perms in ROLE_PERMISSIONS.items()
    ]
