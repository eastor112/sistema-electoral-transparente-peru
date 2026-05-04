"""Integration tests for cédula electoral HTTP routes.

Uses FastAPI TestClient with dependency overrides — no real DB or R2.
The StubX classes replicate the ones in test_cedula_domain.py so each test
module remains self-contained and runnable in isolation.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, date, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from election_system.application.services.cedula_service import CedulaService
from election_system.application.services.partido_service import PartidoService
from election_system.domain.models import (
    Candidato,
    EstadoProceso,
    ListaElectoral,
    PartidoPolitico,
    ProcesoElectoral,
    TipoCargo,
    cargo_tiene_voto_preferencial,
)
from election_system.main import app

# ---------------------------------------------------------------------------
# Minimal stubs (same contract as test_cedula_domain.py, kept local)
# ---------------------------------------------------------------------------


def _now() -> datetime:
    return datetime.now(UTC)


class _PartidoRepo:
    def __init__(self, partidos: list[PartidoPolitico] | None = None) -> None:
        self._store: list[PartidoPolitico] = list(partidos or [])

    async def create(self, *, nombre: str, numero: int) -> PartidoPolitico:
        p = PartidoPolitico(
            partido_id=str(uuid.uuid4()),
            nombre=nombre,
            numero=numero,
            simbolo_url=None,
            activo=True,
            created_at=_now(),
        )
        self._store.append(p)
        return p

    async def get_by_id(self, partido_id: str) -> PartidoPolitico | None:
        return next((p for p in self._store if p.partido_id == partido_id), None)

    async def list_all(self, *, only_active: bool) -> list[PartidoPolitico]:
        return [p for p in self._store if not only_active or p.activo]

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


class _ProcesoRepo:
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
            created_at=_now(),
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
        la = ListaElectoral(
            lista_id=str(uuid.uuid4()),
            proceso_id=proceso_id,
            partido_id=partido_id,
            tipo_cargo=tipo_cargo,
            tiene_voto_preferencial=cargo_tiene_voto_preferencial(tipo_cargo),
        )
        self._listas.append(la)
        return la

    async def get_lista(self, lista_id: str) -> ListaElectoral | None:
        return next((la for la in self._listas if la.lista_id == lista_id), None)

    async def list_listas(self, proceso_id: str) -> list[ListaElectoral]:
        return [la for la in self._listas if la.proceso_id == proceso_id]

    async def add_candidato(
        self, *, lista_id: str, nombre_completo: str, orden: int, es_titular: bool
    ) -> Candidato:
        c = Candidato(
            candidato_id=str(uuid.uuid4()),
            lista_id=lista_id,
            nombre_completo=nombre_completo,
            orden=orden,
            es_titular=es_titular,
            foto_url=None,
            created_at=_now(),
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


class _Storage:
    async def upload_image(
        self,
        *,
        folder: str,
        data: bytes,
        content_type: str,
        original_filename: str = "",
    ) -> str:
        return f"https://assets.example.com/{folder}/file.png"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def partidos_repo() -> _PartidoRepo:
    return _PartidoRepo()


@pytest.fixture()
def proceso_repo() -> _ProcesoRepo:
    return _ProcesoRepo()


@pytest.fixture()
def storage() -> _Storage:
    return _Storage()


@pytest.fixture()
def client(
    partidos_repo: _PartidoRepo,
    proceso_repo: _ProcesoRepo,
    storage: _Storage,
) -> Generator[TestClient, None, None]:
    """TestClient with all DB/storage deps overridden by in-memory stubs."""
    from election_system.api.v1.routes import candidatos, cedula, partidos, procesos

    def _override_cedula_svc() -> CedulaService:
        return CedulaService(
            repository=proceso_repo,
            partido_repository=partidos_repo,
            storage=storage,
        )

    def _override_partido_svc() -> PartidoService:
        return PartidoService(repository=partidos_repo, storage=storage)

    app.dependency_overrides[procesos._build_service] = _override_cedula_svc
    app.dependency_overrides[cedula._build_service] = _override_cedula_svc
    app.dependency_overrides[candidatos._build_service] = _override_cedula_svc
    app.dependency_overrides[partidos._build_service] = _override_partido_svc

    yield TestClient(app)

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper — seed a proceso with one lista and two candidatos
# ---------------------------------------------------------------------------


def _seed(
    client: TestClient,
    proceso_repo: _ProcesoRepo,
    partidos_repo: _PartidoRepo,
) -> dict[str, Any]:
    """Creates a proceso, partido, lista, and two candidatos via the API.

    Returns a dict with all created IDs for use in assertions.
    """
    # Create partido via service directly (partido repo is shared)
    import asyncio

    partido = asyncio.get_event_loop().run_until_complete(
        partidos_repo.create(nombre="Fuerza Popular", numero=3)
    )

    # Create proceso
    r = client.post(
        "/api/v1/procesos",
        json={
            "nombre": "Generales 2026",
            "fecha_jornada": "2026-06-06",
            "tipos_cargo": ["PRESIDENTE_VICEPRESIDENTE"],
        },
    )
    assert r.status_code == 201, r.json()
    proceso_id: str = r.json()["proceso_id"]

    # Create lista
    r = client.post(
        f"/api/v1/procesos/{proceso_id}/listas",
        json={"partido_id": partido.partido_id, "tipo_cargo": "PRESIDENTE_VICEPRESIDENTE"},
    )
    assert r.status_code == 201, r.json()
    lista_id: str = r.json()["lista_id"]

    # Create candidatos
    r1 = client.post(
        f"/api/v1/procesos/{proceso_id}/listas/{lista_id}/candidatos",
        json={"nombre_completo": "Titular Uno", "orden": 1, "es_titular": True},
    )
    assert r1.status_code == 201, r1.json()

    r2 = client.post(
        f"/api/v1/procesos/{proceso_id}/listas/{lista_id}/candidatos",
        json={"nombre_completo": "Suplente Uno", "orden": 1, "es_titular": False},
    )
    assert r2.status_code == 201, r2.json()

    return {
        "partido_id": partido.partido_id,
        "proceso_id": proceso_id,
        "lista_id": lista_id,
        "candidato_titular_id": r1.json()["candidato_id"],
        "candidato_suplente_id": r2.json()["candidato_id"],
    }


# ===========================================================================
# Partidos routes
# ===========================================================================


class TestPartidosRoutes:
    def test_create_partido_returns_201(self, client: TestClient) -> None:
        r = client.post("/api/v1/partidos", json={"nombre": "Partido Demo", "numero": 5})
        assert r.status_code == 201
        body = r.json()
        assert body["nombre"] == "Partido Demo"
        assert body["numero"] == 5
        assert body["activo"] is True
        assert "partido_id" in body

    def test_create_partido_duplicate_numero_returns_409(self, client: TestClient) -> None:
        client.post("/api/v1/partidos", json={"nombre": "Partido A", "numero": 10})
        r = client.post("/api/v1/partidos", json={"nombre": "Partido B", "numero": 10})
        assert r.status_code == 409

    def test_list_partidos_empty(self, client: TestClient) -> None:
        r = client.get("/api/v1/partidos")
        assert r.status_code == 200
        assert r.json() == []

    def test_list_partidos_shows_created(self, client: TestClient) -> None:
        client.post("/api/v1/partidos", json={"nombre": "Accion Popular", "numero": 2})
        r = client.get("/api/v1/partidos")
        assert r.status_code == 200
        names = [p["nombre"] for p in r.json()]
        assert "Accion Popular" in names

    def test_get_partido_not_found_returns_404(self, client: TestClient) -> None:
        r = client.get("/api/v1/partidos/nonexistent")
        assert r.status_code == 404

    def test_upload_simbolo_too_large_returns_413(self, client: TestClient) -> None:
        from election_system.infrastructure.storage.r2_client import MAX_UPLOAD_BYTES

        r_create = client.post("/api/v1/partidos", json={"nombre": "Partido T", "numero": 99})
        partido_id = r_create.json()["partido_id"]

        oversized = b"\x89PNG\r\n\x1a\n" + b"x" * MAX_UPLOAD_BYTES
        r = client.patch(
            f"/api/v1/partidos/{partido_id}/simbolo",
            files={"file": ("logo.png", oversized, "image/png")},
        )
        assert r.status_code == 413

    def test_upload_simbolo_ok_returns_url(self, client: TestClient) -> None:
        r_create = client.post("/api/v1/partidos", json={"nombre": "Partido U", "numero": 42})
        partido_id = r_create.json()["partido_id"]

        valid_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
        r = client.patch(
            f"/api/v1/partidos/{partido_id}/simbolo",
            files={"file": ("logo.png", valid_png, "image/png")},
        )
        assert r.status_code == 200
        assert "simbolo_url" in r.json()


# ===========================================================================
# Procesos routes
# ===========================================================================


class TestProcesosRoutes:
    def test_create_proceso_returns_201(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/procesos",
            json={
                "nombre": "Elecciones 2026",
                "fecha_jornada": "2026-06-06",
                "tipos_cargo": ["PRESIDENTE_VICEPRESIDENTE"],
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["nombre"] == "Elecciones 2026"
        assert body["estado"] == "CONFIGURACION"
        assert "proceso_id" in body

    def test_list_procesos_returns_created(self, client: TestClient) -> None:
        client.post(
            "/api/v1/procesos",
            json={
                "nombre": "Proceso Lista",
                "fecha_jornada": "2026-06-06",
                "tipos_cargo": ["SENADOR_NACIONAL"],
            },
        )
        r = client.get("/api/v1/procesos")
        assert r.status_code == 200
        assert any(p["nombre"] == "Proceso Lista" for p in r.json())

    def test_get_proceso_not_found_returns_404(self, client: TestClient) -> None:
        r = client.get("/api/v1/procesos/ghost")
        assert r.status_code == 404

    def test_update_estado_returns_204(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/procesos",
            json={
                "nombre": "Proceso Estado",
                "fecha_jornada": "2026-06-06",
                "tipos_cargo": ["PRESIDENTE_VICEPRESIDENTE"],
            },
        )
        proceso_id = r.json()["proceso_id"]
        r2 = client.patch(
            f"/api/v1/procesos/{proceso_id}/estado",
            json={"estado": "PUBLICADO"},
        )
        assert r2.status_code == 204

    def test_create_lista_returns_201(
        self,
        client: TestClient,
        proceso_repo: _ProcesoRepo,
        partidos_repo: _PartidoRepo,
    ) -> None:
        ids = _seed(client, proceso_repo, partidos_repo)
        r = client.get(f"/api/v1/procesos/{ids['proceso_id']}/listas")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_create_lista_wrong_cargo_returns_409(
        self,
        client: TestClient,
        proceso_repo: _ProcesoRepo,
        partidos_repo: _PartidoRepo,
    ) -> None:
        ids = _seed(client, proceso_repo, partidos_repo)
        r = client.post(
            f"/api/v1/procesos/{ids['proceso_id']}/listas",
            json={
                "partido_id": ids["partido_id"],
                "tipo_cargo": "SENADOR_NACIONAL",  # not in this proceso
            },
        )
        assert r.status_code == 409

    def test_add_candidato_returns_201(
        self,
        client: TestClient,
        proceso_repo: _ProcesoRepo,
        partidos_repo: _PartidoRepo,
    ) -> None:
        ids = _seed(client, proceso_repo, partidos_repo)
        r = client.post(
            f"/api/v1/procesos/{ids['proceso_id']}/listas/{ids['lista_id']}/candidatos",
            json={"nombre_completo": "Candidato Nuevo", "orden": 2, "es_titular": True},
        )
        assert r.status_code == 201
        assert r.json()["nombre_completo"] == "Candidato Nuevo"

    def test_add_candidato_duplicate_orden_returns_409(
        self,
        client: TestClient,
        proceso_repo: _ProcesoRepo,
        partidos_repo: _PartidoRepo,
    ) -> None:
        ids = _seed(client, proceso_repo, partidos_repo)
        # titular orden 1 already exists from seed
        r = client.post(
            f"/api/v1/procesos/{ids['proceso_id']}/listas/{ids['lista_id']}/candidatos",
            json={"nombre_completo": "Duplicado", "orden": 1, "es_titular": True},
        )
        assert r.status_code == 409

    def test_list_candidatos_returns_seeded(
        self,
        client: TestClient,
        proceso_repo: _ProcesoRepo,
        partidos_repo: _PartidoRepo,
    ) -> None:
        ids = _seed(client, proceso_repo, partidos_repo)
        r = client.get(
            f"/api/v1/procesos/{ids['proceso_id']}/listas/{ids['lista_id']}/candidatos",
        )
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_candidato_idor_wrong_proceso_returns_404(
        self,
        client: TestClient,
        proceso_repo: _ProcesoRepo,
        partidos_repo: _PartidoRepo,
    ) -> None:
        ids = _seed(client, proceso_repo, partidos_repo)
        r = client.post(
            f"/api/v1/procesos/wrong-proc-id/listas/{ids['lista_id']}/candidatos",
            json={"nombre_completo": "IDOR Test", "orden": 99, "es_titular": True},
        )
        assert r.status_code == 404


# ===========================================================================
# Cédula route
# ===========================================================================


class TestCedulaRoute:
    def test_get_cedula_returns_200_with_full_structure(
        self,
        client: TestClient,
        proceso_repo: _ProcesoRepo,
        partidos_repo: _PartidoRepo,
    ) -> None:
        ids = _seed(client, proceso_repo, partidos_repo)
        r = client.get(f"/api/v1/cedula/{ids['proceso_id']}")
        assert r.status_code == 200
        body = r.json()
        assert body["proceso_id"] == ids["proceso_id"]
        assert "listas" in body
        assert len(body["listas"]) == 1
        lista = body["listas"][0]
        # New enriched partido object
        assert "partido" in lista
        assert lista["partido"]["nombre"] == "Fuerza Popular"
        assert lista["partido"]["numero"] == 3
        # Candidatos present
        assert len(lista["candidatos"]) == 2

    def test_get_cedula_titulares_before_suplentes(
        self,
        client: TestClient,
        proceso_repo: _ProcesoRepo,
        partidos_repo: _PartidoRepo,
    ) -> None:
        ids = _seed(client, proceso_repo, partidos_repo)
        r = client.get(f"/api/v1/cedula/{ids['proceso_id']}")
        candidatos = r.json()["listas"][0]["candidatos"]
        titulares_idx = [i for i, c in enumerate(candidatos) if c["es_titular"]]
        suplentes_idx = [i for i, c in enumerate(candidatos) if not c["es_titular"]]
        if titulares_idx and suplentes_idx:
            assert max(titulares_idx) < min(suplentes_idx)

    def test_get_cedula_not_found_returns_404(self, client: TestClient) -> None:
        r = client.get("/api/v1/cedula/ghost-proceso")
        assert r.status_code == 404

    def test_get_cedula_has_generated_at_field(
        self,
        client: TestClient,
        proceso_repo: _ProcesoRepo,
        partidos_repo: _PartidoRepo,
    ) -> None:
        ids = _seed(client, proceso_repo, partidos_repo)
        r = client.get(f"/api/v1/cedula/{ids['proceso_id']}")
        assert "generated_at" in r.json()
