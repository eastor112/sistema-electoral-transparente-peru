from typing import Protocol


class MesaRepositoryPort(Protocol):
    async def exists(self, mesa_id: str) -> bool: ...
