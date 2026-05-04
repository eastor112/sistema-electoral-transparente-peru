"""Use cases for managing partidos políticos and asset uploads."""

from dataclasses import dataclass

from election_system.application.ports import PartidoRepositoryPort, StoragePort
from election_system.core.exceptions import ConflictError, NotFoundError
from election_system.domain.models import PartidoPolitico


@dataclass(frozen=True)
class CreatePartidoResult:
    partido: PartidoPolitico


class PartidoService:
    def __init__(
        self,
        *,
        repository: PartidoRepositoryPort,
        storage: StoragePort,
    ) -> None:
        self._repo = repository
        self._storage = storage

    async def create_partido(
        self, *, nombre: str, numero: int
    ) -> PartidoPolitico:
        existing = await self._repo.list_all(only_active=False)
        if any(p.numero == numero for p in existing):
            raise ConflictError(f"Ya existe un partido con número {numero}.")
        if any(p.nombre.lower() == nombre.lower() for p in existing):
            raise ConflictError(f"Ya existe un partido con nombre {nombre!r}.")
        return await self._repo.create(nombre=nombre, numero=numero)

    async def list_partidos(self, *, only_active: bool = True) -> list[PartidoPolitico]:
        return await self._repo.list_all(only_active=only_active)

    async def get_partido(self, partido_id: str) -> PartidoPolitico:
        partido = await self._repo.get_by_id(partido_id)
        if partido is None:
            raise NotFoundError(f"Partido {partido_id!r} no encontrado.")
        return partido

    async def upload_simbolo(
        self,
        *,
        partido_id: str,
        data: bytes,
        content_type: str,
        original_filename: str,
    ) -> str:
        """Upload party symbol to R2 and persist the URL. Returns new URL."""
        await self.get_partido(partido_id)  # raises NotFoundError if missing
        url = await self._storage.upload_image(
            folder=f"simbolos/{partido_id}",
            data=data,
            content_type=content_type,
            original_filename=original_filename,
        )
        await self._repo.update_simbolo_url(partido_id=partido_id, simbolo_url=url)
        return url
