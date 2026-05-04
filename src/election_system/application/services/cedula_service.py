"""Use cases for managing procesos electorales, listas and candidatos."""

from election_system.application.ports import ProcesoRepositoryPort, StoragePort
from election_system.core.exceptions import ConflictError, NotFoundError
from election_system.domain.models import (
    Candidato,
    EstadoProceso,
    ListaElectoral,
    ProcesoElectoral,
    TipoCargo,
    cargo_tiene_voto_preferencial,
)


class CedulaService:
    def __init__(
        self,
        *,
        repository: ProcesoRepositoryPort,
        storage: StoragePort,
    ) -> None:
        self._repo = repository
        self._storage = storage

    # ------------------------------------------------------------------
    # Procesos
    # ------------------------------------------------------------------

    async def create_proceso(
        self,
        *,
        nombre: str,
        fecha_jornada: str,
        tipos_cargo: list[TipoCargo],
    ) -> ProcesoElectoral:
        return await self._repo.create(
            nombre=nombre,
            fecha_jornada=fecha_jornada,
            tipos_cargo=tipos_cargo,
        )

    async def list_procesos(self) -> list[ProcesoElectoral]:
        return await self._repo.list_all()

    async def get_proceso(self, proceso_id: str) -> ProcesoElectoral:
        proceso = await self._repo.get_by_id(proceso_id)
        if proceso is None:
            raise NotFoundError(f"Proceso {proceso_id!r} no encontrado.")
        return proceso

    async def update_estado(
        self, *, proceso_id: str, estado: EstadoProceso
    ) -> None:
        await self.get_proceso(proceso_id)
        await self._repo.update_estado(proceso_id=proceso_id, estado=estado)

    # ------------------------------------------------------------------
    # Listas electorales
    # ------------------------------------------------------------------

    async def create_lista(
        self,
        *,
        proceso_id: str,
        partido_id: str,
        tipo_cargo: TipoCargo,
    ) -> ListaElectoral:
        proceso = await self.get_proceso(proceso_id)
        if tipo_cargo not in proceso.tipos_cargo:
            raise ConflictError(
                f"El tipo de cargo {tipo_cargo!r} no pertenece al proceso {proceso_id!r}."
            )
        listas = await self._repo.list_listas(proceso_id)
        if any(
            la.partido_id == partido_id and la.tipo_cargo == tipo_cargo
            for la in listas
        ):
            raise ConflictError(
                f"El partido {partido_id!r} ya tiene una lista para {tipo_cargo!r} "
                f"en el proceso {proceso_id!r}."
            )
        return await self._repo.create_lista(
            proceso_id=proceso_id,
            partido_id=partido_id,
            tipo_cargo=tipo_cargo,
        )

    async def list_listas(self, proceso_id: str) -> list[ListaElectoral]:
        await self.get_proceso(proceso_id)
        return await self._repo.list_listas(proceso_id)

    async def get_lista(self, lista_id: str) -> ListaElectoral:
        lista = await self._repo.get_lista(lista_id)
        if lista is None:
            raise NotFoundError(f"Lista {lista_id!r} no encontrada.")
        return lista

    # ------------------------------------------------------------------
    # Candidatos
    # ------------------------------------------------------------------

    async def add_candidato(
        self,
        *,
        lista_id: str,
        nombre_completo: str,
        orden: int,
        es_titular: bool,
    ) -> Candidato:
        await self.get_lista(lista_id)
        candidatos = await self._repo.list_candidatos(lista_id)
        if any(c.orden == orden and c.es_titular == es_titular for c in candidatos):
            kind = "titular" if es_titular else "suplente"
            raise ConflictError(
                f"Ya existe un candidato {kind} con orden {orden} en la lista {lista_id!r}."
            )
        return await self._repo.add_candidato(
            lista_id=lista_id,
            nombre_completo=nombre_completo,
            orden=orden,
            es_titular=es_titular,
        )

    async def get_candidato(self, candidato_id: str) -> Candidato:
        candidato = await self._repo.get_candidato(candidato_id)
        if candidato is None:
            raise NotFoundError(f"Candidato {candidato_id!r} no encontrado.")
        return candidato

    async def list_candidatos(self, lista_id: str) -> list[Candidato]:
        await self.get_lista(lista_id)
        return await self._repo.list_candidatos(lista_id)

    async def upload_foto_candidato(
        self,
        *,
        candidato_id: str,
        data: bytes,
        content_type: str,
        original_filename: str,
    ) -> str:
        await self.get_candidato(candidato_id)
        url = await self._storage.upload_image(
            folder=f"candidatos/{candidato_id}",
            data=data,
            content_type=content_type,
            original_filename=original_filename,
        )
        await self._repo.update_candidato_foto_url(
            candidato_id=candidato_id, foto_url=url
        )
        return url

    # ------------------------------------------------------------------
    # Vista de cédula completa
    # ------------------------------------------------------------------

    async def get_cedula(self, proceso_id: str) -> "CedulaView":
        proceso = await self.get_proceso(proceso_id)
        listas = await self._repo.list_listas(proceso_id)
        listas_con_candidatos: list[ListaElectoral] = []
        for lista in listas:
            candidatos = await self._repo.list_candidatos(lista.lista_id)

            listas_con_candidatos.append(
                ListaElectoral(
                    lista_id=lista.lista_id,
                    proceso_id=lista.proceso_id,
                    partido_id=lista.partido_id,
                    tipo_cargo=lista.tipo_cargo,
                    tiene_voto_preferencial=cargo_tiene_voto_preferencial(lista.tipo_cargo),
                    candidatos=sorted(candidatos, key=lambda c: (c.es_titular, c.orden)),
                )
            )
        return CedulaView(proceso=proceso, listas=listas_con_candidatos)


from dataclasses import dataclass  # noqa: E402


@dataclass(frozen=True)
class CedulaView:
    proceso: ProcesoElectoral
    listas: list[ListaElectoral]
