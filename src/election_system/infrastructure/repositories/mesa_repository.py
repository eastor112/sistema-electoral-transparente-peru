from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from election_system.infrastructure.db.models import MesaORM


class MesaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, mesa_id: str) -> bool:
        stmt = select(MesaORM.mesa_id).where(MesaORM.mesa_id == mesa_id).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
