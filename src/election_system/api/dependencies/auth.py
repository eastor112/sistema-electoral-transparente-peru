from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Annotated, Any

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.core.security import decode_token
from election_system.domain.models import Permission, RoleType, UserRole
from election_system.infrastructure.db.session import get_db_session
from election_system.infrastructure.repositories.role_repository import RoleRepository


@dataclass(frozen=True)
class CurrentActor:
    """Authenticated principal with resolved roles and permissions."""

    actor_id: str
    roles: list[UserRole] = field(default_factory=list)

    @property
    def role_types(self) -> frozenset[RoleType]:
        return frozenset(r.role_type for r in self.roles)

    @property
    def permissions(self) -> frozenset[Permission]:
        result: set[Permission] = set()
        for role in self.roles:
            result.update(role.permissions)
        return frozenset(result)

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

    def has_any_role(self, *role_types: RoleType) -> bool:
        return bool(self.role_types.intersection(role_types))


async def get_current_actor(
    *,
    authorization: Annotated[str | None, Header()] = None,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CurrentActor:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
        )

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token, expected_type="access")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    repo = RoleRepository(session)
    roles = await repo.get_active_roles_for_user(subject)
    return CurrentActor(actor_id=subject, roles=roles)


def require_roles(
    *role_types: RoleType,
) -> Callable[[CurrentActor], Coroutine[Any, Any, CurrentActor]]:
    """Dependency factory that enforces the actor has at least one of the given roles."""

    async def _check(
        actor: Annotated[CurrentActor, Depends(get_current_actor)],
    ) -> CurrentActor:
        if not actor.has_any_role(*role_types):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role for this operation",
            )
        return actor

    return _check


def require_permissions(
    *permissions: Permission,
) -> Callable[[CurrentActor], Coroutine[Any, Any, CurrentActor]]:
    """Dependency factory that enforces the actor has ALL of the given permissions."""

    async def _check(
        actor: Annotated[CurrentActor, Depends(get_current_actor)],
    ) -> CurrentActor:
        missing = [p for p in permissions if not actor.has_permission(p)]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation",
            )
        return actor

    return _check
