"""Unit tests for cédula electoral domain logic and service layer.

Uses in-memory stubs — no database, no network.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

import pytest

from election_system.application.services.cedula_service import (
    CedulaService,
    CedulaView,
    ListaConPartido,
)
from election_system.application.services.partido_service import PartidoService
from election_system.core.exceptions import ConflictError, NotFoundError
from election_system.domain.models import (
    Candidato,
    EstadoProceso,
    ListaElectoral,
    PartidoPolitico,
    ProcesoElectoral,
    TipoCargo,
    cargo_tiene_voto_preferencial,
)
from election_system.infrastructure.storage.r2_client import (
    MAX_UPLOAD_BYTES,
    _check_magic_bytes,
)

# ---------------------------------------------------------------------------
# Helpers / Fakes
# ---------------------------------------------------------------------------


def _make_partido(
    *,
    partido_id: str | None = None,
    nombre: str = "Partido A",
    numero: int = 1,
    simbolo_url: str | None = None,
    activo: bool = True,
) -> PartidoPolitico:
    return PartidoPolitico(
        partido_id=partido_id or str(uuid.uuid4()),
        nombre=nombre,
        numero=numero,
        simbolo_url=simbolo_url,
        activo=activo,
        created_at=datetime.now(UTC),
    )


def _make_proceso(
    *,
    proceso_id: str | None = None,
    tipos_cargo: list[TipoCargo] | None = None,
    estado: EstadoProceso = EstadoProceso.CONFIGURACION,
    fecha_jornada: date | None = None,
) -> ProcesoElectoral:
    return ProcesoElectoral(
        proceso_id=proceso_id or str(uuid.uuid4()),
        nombre="Elecciones Generales 2026",
        fecha_jornada=fecha_jornada or date(2026, 6, 6),
        tipos_cargo=tipos_cargo or [TipoCargo.PRESIDENTE_VICEPRESIDENTE],
        estado=estado,
        created_at=datetime.now(UTC),
    )


def _make_lista(
    *,
    lista_id: str | None = None,
    proceso_id: str = "proc-1",
    partido_id: str = "part-1",
    tipo_cargo: TipoCargo = TipoCargo.PRESIDENTE_VICEPRESIDENTE,
) -> ListaElectoral:
    return ListaElectoral(
        lista_id=lista_id or str(uuid.uuid4()),
        proceso_id=proceso_id,
        partido_id=partido_id,
        tipo_cargo=tipo_cargo,
        tiene_voto_preferencial=cargo_tiene_voto_preferencial(tipo_cargo),
    )


def _make_candidato(
    *,
    candidato_id: str | None = None,
    lista_id: str = "lista-1",
    nombre_completo: str = "Juan Pérez",
    orden: int = 1,
    es_titular: bool = True,
    foto_url: str | None = None,
) -> Candidato:
    return Candidato(
        candidato_id=candidato_id or str(uuid.uuid4()),
        lista_id=lista_id,
        nombre_completo=nombre_completo,
        orden=orden,
        es_titular=es_titular,
        foto_url=foto_url,
        created_at=datetime.now(UTC),
    )


# ---------------------------------------------------------------------------
# Stub repositories / storage (in-memory)
# ---------------------------------------------------------------------------


class StubPartidoRepository:
    def __init__(self, partidos: list[PartidoPolitico] | None = None) -> None:
        self._store: list[PartidoPolitico] = list(partidos or [])

    async def create(self, *, nombre: str, numero: int) -> PartidoPolitico:
        p = _make_partido(partido_id=str(uuid.uuid4()), nombre=nombre, numero=numero)
        self._store.append(p)
        return p

    async def get_by_id(self, partido_id: str) -> PartidoPolitico | None:
        return next((p for p in self._store if p.partido_id == partido_id), None)

    async def list_all(self, *, only_active: bool) -> list[PartidoPolitico]:
        return [p for p in self._store if (not only_active or p.activo)]

    async def update_simbolo_url(self, *, partido_id: str, simbolo_url: str) -> None:
        self._store = [
            PartidoPolitico(
                partido_id=p.partido_id,
                nombre=p.nombre,
                numero=p.numero,
                simbolo_url=simbolo_url if p.partido_id == partido_id else p.simbolo_url,
                activo=p.activo,
                created_at=p.created_at,
            )
            for p in self._store
        ]


class StubProcesoRepository:
    def __init__(self) -> None:
        self._procesos: list[ProcesoElectoral] = []
        self._listas: list[ListaElectoral] = []
        self._candidatos: list[Candidato] = []

    async def create(
        self, *, nombre: str, fecha_jornada: str, tipos_cargo: list[TipoCargo]
    ) -> ProcesoElectoral:
        p = ProcesoElectoral(
            proceso_id=str(uuid.uuid4()),
            nombre=nombre,
            fecha_jornada=date.fromisoformat(fecha_jornada),
            tipos_cargo=tipos_cargo,
            estado=EstadoProceso.CONFIGURACION,
            created_at=datetime.now(UTC),
        )
        self._procesos.append(p)
        return p

    async def get_by_id(self, proceso_id: str) -> ProcesoElectoral | None:
        return next((p for p in self._procesos if p.proceso_id == proceso_id), None)

    async def list_all(self) -> list[ProcesoElectoral]:
        return list(self._procesos)

    async def update_estado(self, *, proceso_id: str, estado: EstadoProceso) -> None:
        self._procesos = [
            ProcesoElectoral(
                proceso_id=p.proceso_id,
                nombre=p.nombre,
                fecha_jornada=p.fecha_jornada,
                tipos_cargo=p.tipos_cargo,
                estado=estado if p.proceso_id == proceso_id else p.estado,
                created_at=p.created_at,
            )
            for p in self._procesos
        ]

    async def create_lista(
        self, *, proceso_id: str, partido_id: str, tipo_cargo: TipoCargo
    ) -> ListaElectoral:
        la = _make_lista(
            lista_id=str(uuid.uuid4()),
            proceso_id=proceso_id,
            partido_id=partido_id,
            tipo_cargo=tipo_cargo,
        )
        self._listas.append(la)
        return la

    async def get_lista(self, lista_id: str) -> ListaElectoral | None:
        return next((la for la in self._listas if la.lista_id == lista_id), None)

    async def list_listas(self, proceso_id: str) -> list[ListaElectoral]:
        return [la for la in self._listas if la.proceso_id == proceso_id]

    async def add_candidato(
        self,
        *,
        lista_id: str,
        nombre_completo: str,
        orden: int,
        es_titular: bool,
    ) -> Candidato:
        c = _make_candidato(
            candidato_id=str(uuid.uuid4()),
            lista_id=lista_id,
            nombre_completo=nombre_completo,
            orden=orden,
            es_titular=es_titular,
        )
        self._candidatos.append(c)
        return c

    async def get_candidato(self, candidato_id: str) -> Candidato | None:
        return next((c for c in self._candidatos if c.candidato_id == candidato_id), None)

    async def list_candidatos(self, lista_id: str) -> list[Candidato]:
        return [c for c in self._candidatos if c.lista_id == lista_id]

    async def update_candidato_foto_url(self, *, candidato_id: str, foto_url: str) -> None:
        self._candidatos = [
            Candidato(
                candidato_id=c.candidato_id,
                lista_id=c.lista_id,
                nombre_completo=c.nombre_completo,
                orden=c.orden,
                es_titular=c.es_titular,
                foto_url=foto_url if c.candidato_id == candidato_id else c.foto_url,
                created_at=c.created_at,
            )
            for c in self._candidatos
        ]


class StubStorage:
    """Captures upload calls; returns deterministic URLs."""

    def __init__(self) -> None:
        self.uploads: list[dict[str, object]] = []

    async def upload_image(
        self,
        *,
        folder: str,
        data: bytes,
        content_type: str,
        original_filename: str = "",
    ) -> str:
        self.uploads.append(
            {"folder": folder, "content_type": content_type, "size": len(data)}
        )
        return f"https://assets.example.com/{folder}/image.png"


# ---------------------------------------------------------------------------
# Helper — build CedulaService with stubs
# ---------------------------------------------------------------------------


def _cedula_service(
    *,
    procesos: StubProcesoRepository | None = None,
    partidos: StubPartidoRepository | None = None,
    storage: StubStorage | None = None,
) -> CedulaService:
    return CedulaService(
        repository=procesos or StubProcesoRepository(),
        partido_repository=partidos or StubPartidoRepository(),
        storage=storage or StubStorage(),
    )


# ===========================================================================
# Domain rules
# ===========================================================================


class TestCargoTieneVotoPreferencial:
    def test_presidente_no_tiene_voto_preferencial(self) -> None:
        assert not cargo_tiene_voto_preferencial(TipoCargo.PRESIDENTE_VICEPRESIDENTE)

    def test_senador_nacional_tiene_voto_preferencial(self) -> None:
        assert cargo_tiene_voto_preferencial(TipoCargo.SENADOR_NACIONAL)

    def test_senador_universo_tiene_voto_preferencial(self) -> None:
        assert cargo_tiene_voto_preferencial(TipoCargo.SENADOR_UNIVERSO)

    def test_diputado_universo_tiene_voto_preferencial(self) -> None:
        assert cargo_tiene_voto_preferencial(TipoCargo.DIPUTADO_UNIVERSO)

    def test_parlamento_andino_tiene_voto_preferencial(self) -> None:
        assert cargo_tiene_voto_preferencial(TipoCargo.PARLAMENTO_ANDINO)


# ===========================================================================
# Magic bytes guard
# ===========================================================================


class TestMagicBytes:
    def test_valid_jpeg(self) -> None:
        assert _check_magic_bytes(b"\xff\xd8\xff\xe0extra", "image/jpeg")

    def test_invalid_jpeg(self) -> None:
        assert not _check_magic_bytes(b"\x89PNG\r\n\x1a\n", "image/jpeg")

    def test_valid_png(self) -> None:
        assert _check_magic_bytes(b"\x89PNG\r\n\x1a\ndata", "image/png")

    def test_invalid_png(self) -> None:
        assert not _check_magic_bytes(b"\xff\xd8\xff", "image/png")

    def test_valid_webp(self) -> None:
        assert _check_magic_bytes(b"RIFF\x00\x00\x00\x00WEBPdata", "image/webp")

    def test_invalid_webp_wrong_riff(self) -> None:
        assert not _check_magic_bytes(b"JUNK\x00\x00\x00\x00WEBPdata", "image/webp")

    def test_valid_svg_lowercase(self) -> None:
        assert _check_magic_bytes(b"<svg xmlns=...", "image/svg+xml")

    def test_valid_svg_xml_declaration(self) -> None:
        assert _check_magic_bytes(b"<?xml version='1.0'?><svg>", "image/svg+xml")

    def test_valid_svg_with_leading_whitespace(self) -> None:
        assert _check_magic_bytes(b"   <svg>", "image/svg+xml")

    def test_invalid_svg_html_content(self) -> None:
        assert not _check_magic_bytes(b"<html><body>xss</body></html>", "image/svg+xml")

    def test_max_upload_bytes_is_5mb(self) -> None:
        assert MAX_UPLOAD_BYTES == 5 * 1024 * 1024


# ===========================================================================
# PartidoService
# ===========================================================================


class TestPartidoService:
    def _service(
        self,
        partidos: list[PartidoPolitico] | None = None,
    ) -> PartidoService:
        return PartidoService(
            repository=StubPartidoRepository(partidos),
            storage=StubStorage(),
        )

    @pytest.mark.asyncio
    async def test_create_partido_ok(self) -> None:
        svc = self._service()
        p = await svc.create_partido(nombre="Alianza Para el Progreso", numero=7)
        assert p.nombre == "Alianza Para el Progreso"
        assert p.numero == 7
        assert p.activo is True

    @pytest.mark.asyncio
    async def test_create_partido_duplicate_numero_raises(self) -> None:
        existing = [_make_partido(nombre="Partido A", numero=7)]
        svc = self._service(existing)
        with pytest.raises(ConflictError, match="número 7"):
            await svc.create_partido(nombre="Partido B", numero=7)

    @pytest.mark.asyncio
    async def test_create_partido_duplicate_nombre_raises(self) -> None:
        existing = [_make_partido(nombre="Fuerza Popular", numero=7)]
        svc = self._service(existing)
        with pytest.raises(ConflictError, match="(?i)fuerza popular"):
            await svc.create_partido(nombre="fuerza popular", numero=8)

    @pytest.mark.asyncio
    async def test_get_partido_not_found_raises(self) -> None:
        svc = self._service()
        with pytest.raises(NotFoundError):
            await svc.get_partido("nonexistent-id")

    @pytest.mark.asyncio
    async def test_list_partidos_filters_by_active(self) -> None:
        partidos = [
            _make_partido(nombre="Activo", numero=1, activo=True),
            _make_partido(nombre="Inactivo", numero=2, activo=False),
        ]
        svc = self._service(partidos)
        activos = await svc.list_partidos(only_active=True)
        todos = await svc.list_partidos(only_active=False)
        assert len(activos) == 1
        assert len(todos) == 2


# ===========================================================================
# CedulaService — procesos
# ===========================================================================


class TestCedulaServiceProcesos:
    @pytest.mark.asyncio
    async def test_create_proceso_ok(self) -> None:
        svc = _cedula_service()
        p = await svc.create_proceso(
            nombre="Generales 2026",
            fecha_jornada="2026-06-06",
            tipos_cargo=[TipoCargo.PRESIDENTE_VICEPRESIDENTE],
        )
        assert p.nombre == "Generales 2026"
        assert p.estado == EstadoProceso.CONFIGURACION

    @pytest.mark.asyncio
    async def test_get_proceso_not_found_raises(self) -> None:
        svc = _cedula_service()
        with pytest.raises(NotFoundError):
            await svc.get_proceso("ghost-id")

    @pytest.mark.asyncio
    async def test_update_estado_persists(self) -> None:
        repo = StubProcesoRepository()
        svc = _cedula_service(procesos=repo)
        p = await svc.create_proceso(
            nombre="Proceso X",
            fecha_jornada="2026-06-06",
            tipos_cargo=[TipoCargo.PRESIDENTE_VICEPRESIDENTE],
        )
        await svc.update_estado(proceso_id=p.proceso_id, estado=EstadoProceso.PUBLICADO)
        updated = await svc.get_proceso(p.proceso_id)
        assert updated.estado == EstadoProceso.PUBLICADO


# ===========================================================================
# CedulaService — listas
# ===========================================================================


class TestCedulaServiceListas:
    @pytest.mark.asyncio
    async def test_create_lista_ok(self) -> None:
        repo = StubProcesoRepository()
        svc = _cedula_service(procesos=repo)
        p = await svc.create_proceso(
            nombre="Proceso",
            fecha_jornada="2026-06-06",
            tipos_cargo=[TipoCargo.PRESIDENTE_VICEPRESIDENTE],
        )
        la = await svc.create_lista(
            proceso_id=p.proceso_id,
            partido_id="part-1",
            tipo_cargo=TipoCargo.PRESIDENTE_VICEPRESIDENTE,
        )
        assert la.proceso_id == p.proceso_id
        assert la.partido_id == "part-1"

    @pytest.mark.asyncio
    async def test_create_lista_wrong_cargo_raises(self) -> None:
        repo = StubProcesoRepository()
        svc = _cedula_service(procesos=repo)
        p = await svc.create_proceso(
            nombre="Proceso",
            fecha_jornada="2026-06-06",
            tipos_cargo=[TipoCargo.PRESIDENTE_VICEPRESIDENTE],
        )
        with pytest.raises(ConflictError, match="no pertenece al proceso"):
            await svc.create_lista(
                proceso_id=p.proceso_id,
                partido_id="part-1",
                tipo_cargo=TipoCargo.SENADOR_NACIONAL,
            )

    @pytest.mark.asyncio
    async def test_create_lista_duplicate_raises(self) -> None:
        repo = StubProcesoRepository()
        svc = _cedula_service(procesos=repo)
        p = await svc.create_proceso(
            nombre="Proceso",
            fecha_jornada="2026-06-06",
            tipos_cargo=[TipoCargo.PRESIDENTE_VICEPRESIDENTE],
        )
        await svc.create_lista(
            proceso_id=p.proceso_id,
            partido_id="part-1",
            tipo_cargo=TipoCargo.PRESIDENTE_VICEPRESIDENTE,
        )
        with pytest.raises(ConflictError, match="ya tiene una lista"):
            await svc.create_lista(
                proceso_id=p.proceso_id,
                partido_id="part-1",
                tipo_cargo=TipoCargo.PRESIDENTE_VICEPRESIDENTE,
            )


# ===========================================================================
# CedulaService — candidatos
# ===========================================================================


class TestCedulaServiceCandidatos:
    async def _setup(self) -> tuple[CedulaService, str, str]:
        """Returns (service, proceso_id, lista_id)."""
        repo = StubProcesoRepository()
        svc = _cedula_service(procesos=repo)
        p = await svc.create_proceso(
            nombre="Proceso",
            fecha_jornada="2026-06-06",
            tipos_cargo=[TipoCargo.PRESIDENTE_VICEPRESIDENTE],
        )
        la = await svc.create_lista(
            proceso_id=p.proceso_id,
            partido_id="part-1",
            tipo_cargo=TipoCargo.PRESIDENTE_VICEPRESIDENTE,
        )
        return svc, p.proceso_id, la.lista_id

    @pytest.mark.asyncio
    async def test_add_candidato_ok(self) -> None:
        svc, proc_id, lista_id = await self._setup()
        c = await svc.add_candidato(
            proceso_id=proc_id,
            lista_id=lista_id,
            nombre_completo="María García",
            orden=1,
            es_titular=True,
        )
        assert c.nombre_completo == "María García"
        assert c.es_titular is True

    @pytest.mark.asyncio
    async def test_add_candidato_duplicate_orden_raises(self) -> None:
        svc, proc_id, lista_id = await self._setup()
        await svc.add_candidato(
            proceso_id=proc_id,
            lista_id=lista_id,
            nombre_completo="Primer Candidato",
            orden=1,
            es_titular=True,
        )
        with pytest.raises(ConflictError, match="orden 1"):
            await svc.add_candidato(
                proceso_id=proc_id,
                lista_id=lista_id,
                nombre_completo="Segundo Candidato",
                orden=1,
                es_titular=True,
            )

    @pytest.mark.asyncio
    async def test_add_candidato_idor_wrong_proceso_raises(self) -> None:
        svc, _proc_id, lista_id = await self._setup()
        with pytest.raises(NotFoundError):
            await svc.add_candidato(
                proceso_id="wrong-proceso-id",
                lista_id=lista_id,
                nombre_completo="Atacante",
                orden=1,
                es_titular=True,
            )

    @pytest.mark.asyncio
    async def test_list_candidatos_idor_wrong_proceso_raises(self) -> None:
        svc, _proc_id, lista_id = await self._setup()
        with pytest.raises(NotFoundError):
            await svc.list_candidatos(lista_id=lista_id, proceso_id="wrong-proceso-id")

    @pytest.mark.asyncio
    async def test_list_candidatos_sorted_titulares_first(self) -> None:
        svc, proc_id, lista_id = await self._setup()
        await svc.add_candidato(
            proceso_id=proc_id,
            lista_id=lista_id,
            nombre_completo="Suplente 1",
            orden=1,
            es_titular=False,
        )
        await svc.add_candidato(
            proceso_id=proc_id,
            lista_id=lista_id,
            nombre_completo="Titular 2",
            orden=2,
            es_titular=True,
        )
        await svc.add_candidato(
            proceso_id=proc_id,
            lista_id=lista_id,
            nombre_completo="Titular 1",
            orden=1,
            es_titular=True,
        )
        # get_cedula sorts titulares first within each lista
        cedula = await svc.get_cedula(proc_id)
        candidatos = cedula.listas[0].candidatos
        titulares = [c for c in candidatos if c.es_titular]
        suplentes = [c for c in candidatos if not c.es_titular]
        # All titulares appear before any suplente
        if titulares and suplentes:
            last_titular_idx = max(candidatos.index(t) for t in titulares)
            first_suplente_idx = min(candidatos.index(s) for s in suplentes)
            assert last_titular_idx < first_suplente_idx


# ===========================================================================
# CedulaService — get_cedula (enriched view)
# ===========================================================================


class TestCedulaView:
    @pytest.mark.asyncio
    async def test_get_cedula_enriches_partido_info(self) -> None:
        partido = _make_partido(
            partido_id="part-1",
            nombre="Fuerza Popular",
            numero=3,
            simbolo_url="https://assets.example.com/simbolos/part-1/logo.png",
        )
        partidos_repo = StubPartidoRepository([partido])
        proceso_repo = StubProcesoRepository()
        svc = _cedula_service(procesos=proceso_repo, partidos=partidos_repo)

        p = await svc.create_proceso(
            nombre="Generales 2026",
            fecha_jornada="2026-06-06",
            tipos_cargo=[TipoCargo.PRESIDENTE_VICEPRESIDENTE],
        )
        await svc.create_lista(
            proceso_id=p.proceso_id,
            partido_id="part-1",
            tipo_cargo=TipoCargo.PRESIDENTE_VICEPRESIDENTE,
        )
        cedula = await svc.get_cedula(p.proceso_id)

        assert isinstance(cedula, CedulaView)
        assert len(cedula.listas) == 1
        lista = cedula.listas[0]
        assert isinstance(lista, ListaConPartido)
        assert lista.partido.nombre == "Fuerza Popular"
        assert lista.partido.numero == 3
        assert lista.partido.simbolo_url is not None
        assert lista.tiene_voto_preferencial is False

    @pytest.mark.asyncio
    async def test_get_cedula_unknown_partido_uses_defaults(self) -> None:
        """If a partido is not in the catalog, gracefully use placeholder values."""
        svc = _cedula_service()  # empty partidos repo
        p = await svc.create_proceso(
            nombre="Proceso",
            fecha_jornada="2026-06-06",
            tipos_cargo=[TipoCargo.SENADOR_NACIONAL],
        )
        await svc.create_lista(
            proceso_id=p.proceso_id,
            partido_id="missing-party",
            tipo_cargo=TipoCargo.SENADOR_NACIONAL,
        )
        cedula = await svc.get_cedula(p.proceso_id)
        assert cedula.listas[0].partido.nombre == "—"
        assert cedula.listas[0].tiene_voto_preferencial is True

    @pytest.mark.asyncio
    async def test_get_cedula_not_found_raises(self) -> None:
        svc = _cedula_service()
        with pytest.raises(NotFoundError):
            await svc.get_cedula("ghost-proceso")
