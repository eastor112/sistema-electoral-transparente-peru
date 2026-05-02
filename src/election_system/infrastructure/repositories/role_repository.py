from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.domain.models import RoleType, UserRole
from election_system.infrastructure.db.models import UserRoleORM


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_roles_for_user(self, user_id: str) -> list[UserRole]:
        stmt = (
            select(UserRoleORM)
            .where(UserRoleORM.user_id == user_id, UserRoleORM.is_active.is_(True))
            .order_by(UserRoleORM.assigned_at)
        )
        result = await self._session.execute(stmt)
        return [_map_role(row) for row in result.scalars().all()]

    async def get_role(self, user_role_id: str) -> UserRole | None:
        stmt = select(UserRoleORM).where(UserRoleORM.user_role_id == user_role_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return _map_role(row) if row is not None else None

    async def assign_role(
        self,
        *,
        user_id: str,
        role_type: RoleType,
        assigned_by: str,
        mesa_id: str | None,
        ubigeo: str | None,
        jornada_id: str | None,
    ) -> UserRole:
        now = datetime.now(UTC)
        row = UserRoleORM(
            user_role_id=str(uuid4()),
            user_id=user_id,
            role_type=role_type.value,
            mesa_id=mesa_id,
            ubigeo=ubigeo,
            jornada_id=jornada_id,
            is_active=True,
            assigned_by=assigned_by,
            assigned_at=now,
            revoked_at=None,
        )
        self._session.add(row)
        await self._session.flush()
        return _map_role(row)

    async def revoke_role(self, *, user_role_id: str, revoked_at: datetime) -> None:
        stmt = (
            update(UserRoleORM)
            .where(UserRoleORM.user_role_id == user_role_id)
            .values(is_active=False, revoked_at=revoked_at)
        )
        await self._session.execute(stmt)

    async def list_roles(
        self,
        *,
        user_id: str | None,
        role_type: RoleType | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[UserRole]:
        stmt = select(UserRoleORM)
        if user_id is not None:
            stmt = stmt.where(UserRoleORM.user_id == user_id)
        if role_type is not None:
            stmt = stmt.where(UserRoleORM.role_type == role_type.value)
        if is_active is not None:
            stmt = stmt.where(UserRoleORM.is_active.is_(is_active))
        stmt = stmt.order_by(UserRoleORM.assigned_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [_map_role(row) for row in result.scalars().all()]


def _map_role(row: UserRoleORM) -> UserRole:
    return UserRole(
        user_role_id=row.user_role_id,
        user_id=row.user_id,
        role_type=RoleType(row.role_type),
        mesa_id=row.mesa_id,
        ubigeo=row.ubigeo,
        jornada_id=row.jornada_id,
        is_active=row.is_active,
        assigned_by=row.assigned_by,
        assigned_at=row.assigned_at,
        revoked_at=row.revoked_at,
    )
