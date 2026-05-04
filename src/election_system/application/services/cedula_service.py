"""Use cases for managing procesos electorales, listas and candidatos."""

from dataclasses import dataclass

from election_system.application.ports import (
    PartidoRepositoryPort,
    ProcesoRepositoryPort,
    StoragePort,
)
from election_system.core.exceptions import ConflictError, NotFoundError
from election_system.domain.models import (
    Candidato,
    EstadoProceso,
    ListaElectoral,
    ProcesoElectoral,
    TipoCargo,
    cargo_tiene_voto_preferencial,
)

# ---------------------------------------------------------------------------
# View models (application layer — enriched read projections, not domain)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PartidoResumen:
    partido_id: str
    nombre: str
    numero: int
    simbolo_url: str | None


@dataclass(frozen=True)
class ListaConPartido:
    lista_id: str
    proceso_id: str
    partido: PartidoResumen
    tipo_cargo: TipoCargo
    tiene_voto_preferencial: bool
    candidatos: list[Candidato]


@dataclass(frozen=True)
class CedulaView:
    proceso: ProcesoElectoral
    listas: list[ListaConPartido]


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class CedulaService:
    def __init__(
        self,
        *,
        repository: ProcesoRepositoryPort,
        storage: StoragePort,
        partido_repository: PartidoRepositoryPort,
    ) -> None:
        self._repo = repository
        self._storage = storage
        self._partido_repo = partido_repository

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

    async def update_estado(self, *, proceso_id: str, estado: EstadoProceso) -> None:
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
        if any(la.partido_id == partido_id and la.tipo_cargo == tipo_cargo for la in listas):
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
        proceso_id: str,
        lista_id: str,
        nombre_completo: str,
        orden: int,
        es_titular: bool,
    ) -> Candidato:
        lista = await self.get_lista(lista_id)
        # IDOR guard: ensure the lista belongs to the declared proceso
        if lista.proceso_id != proceso_id:
            raise NotFoundError(f"Lista {lista_id!r} no encontrada.")
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

    async def list_candidatos(
        self, *, lista_id: str, proceso_id: str | None = None
    ) -> list[Candidato]:
        lista = await self.get_lista(lista_id)
        # IDOR guard: when proceso_id provided, verify ownership
        if proceso_id is not None and lista.proceso_id != proceso_id:
            raise NotFoundError(f"Lista {lista_id!r} no encontrada.")
        return await self._repo.list_candidatos(lista.lista_id)

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
        await self._repo.update_candidato_foto_url(candidato_id=candidato_id, foto_url=url)
        return url

    # ------------------------------------------------------------------
    # Vista de cédula completa
    # ------------------------------------------------------------------

    async def get_cedula(self, proceso_id: str) -> CedulaView:
        proceso = await self.get_proceso(proceso_id)
        listas = await self._repo.list_listas(proceso_id)

        # Batch-fetch all parties once to avoid N+1 queries
        all_partidos = await self._partido_repo.list_all(only_active=False)
        partido_map = {p.partido_id: p for p in all_partidos}

        listas_enriquecidas: list[ListaConPartido] = []
        for lista in listas:
            # TODO: replace individual candidato queries with a batch query
            #       keyed on proceso_id when load requires it.
            candidatos = await self._repo.list_candidatos(lista.lista_id)
            partido = partido_map.get(lista.partido_id)
            listas_enriquecidas.append(
                ListaConPartido(
                    lista_id=lista.lista_id,
                    proceso_id=lista.proceso_id,
                    partido=PartidoResumen(
                        partido_id=lista.partido_id,
                        nombre=partido.nombre if partido else "—",
                        numero=partido.numero if partido else 0,
                        simbolo_url=partido.simbolo_url if partido else None,
                    ),
                    tipo_cargo=lista.tipo_cargo,
                    tiene_voto_preferencial=cargo_tiene_voto_preferencial(lista.tipo_cargo),
                    # Titulares first: not True == False < True == not False
                    candidatos=sorted(candidatos, key=lambda c: (not c.es_titular, c.orden)),
                )
            )
        return CedulaView(proceso=proceso, listas=listas_enriquecidas)
