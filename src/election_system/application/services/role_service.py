from dataclasses import dataclass
from datetime import UTC, datetime

from election_system.application.ports import RoleRepositoryPort
from election_system.core.exceptions import ConflictError, DomainError
from election_system.domain.models import RoleType, UserRole


class RoleNotFoundError(DomainError):
    pass


@dataclass(frozen=True)
class AssignRoleResult:
    user_role: UserRole


class RoleService:
    def __init__(self, *, repository: RoleRepositoryPort) -> None:
        self._repository = repository

    async def assign_role(
        self,
        *,
        user_id: str,
        role_type: RoleType,
        assigned_by: str,
        mesa_id: str | None = None,
        ubigeo: str | None = None,
        jornada_id: str | None = None,
    ) -> AssignRoleResult:
        # Prevent duplicate active assignment for same scope
        existing = await self._repository.get_active_roles_for_user(user_id)
        for role in existing:
            if (
                role.role_type == role_type
                and role.mesa_id == mesa_id
                and role.ubigeo == ubigeo
                and role.jornada_id == jornada_id
            ):
                raise ConflictError(
                    f"User {user_id!r} already has active role {role_type!r} "
                    f"with the same scope."
                )

        user_role = await self._repository.assign_role(
            user_id=user_id,
            role_type=role_type,
            assigned_by=assigned_by,
            mesa_id=mesa_id,
            ubigeo=ubigeo,
            jornada_id=jornada_id,
        )
        return AssignRoleResult(user_role=user_role)

    async def revoke_role(self, *, user_role_id: str) -> None:
        role = await self._repository.get_role(user_role_id)
        if role is None or not role.is_active:
            raise RoleNotFoundError(
                f"Active role assignment {user_role_id!r} not found."
            )
        await self._repository.revoke_role(
            user_role_id=user_role_id,
            revoked_at=datetime.now(UTC),
        )

    async def get_user_roles(self, user_id: str) -> list[UserRole]:
        return await self._repository.get_active_roles_for_user(user_id)

    async def list_roles(
        self,
        *,
        user_id: str | None = None,
        role_type: RoleType | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
    ) -> list[UserRole]:
        return await self._repository.list_roles(
            user_id=user_id,
            role_type=role_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
