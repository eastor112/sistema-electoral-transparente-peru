# Cédula Electoral + Cloudflare R2

Fecha: 2026-05-04
Estado: completado

## Resumen

Se implemento el sistema completo de cédula electoral digital basado en el modelo peruano.
Permite configurar procesos electorales, partidos políticos con sus símbolos, listas electorales
por tipo de cargo, y candidatos titulares/suplentes con foto. Los assets gráficos se almacenan en
Cloudflare R2 (S3-compatible).

Fuente de diseño: `plans/09-panel-administracion-roles-y-cedula.md`, secciones 1–4.

## Componentes implementados

### Dominio (`domain/models.py`)

| Clase/Enum | Descripción |
|---|---|
| `TipoCargo` | `PRESIDENTE_VICEPRESIDENTE`, `SENADOR_NACIONAL`, `SENADOR_UNIVERSO`, `DIPUTADO_UNIVERSO`, `PARLAMENTO_ANDINO` |
| `EstadoProceso` | `CONFIGURACION` → `PUBLICADO` → `EN_CURSO` → `CERRADO` |
| `PartidoPolitico` | Partido con nombre, número y URL de símbolo |
| `ProcesoElectoral` | Proceso con tipos de cargo y estado de ciclo de vida |
| `ListaElectoral` | Lista de un partido para un tipo de cargo dentro de un proceso |
| `Candidato` | Candidato titular o suplente con orden y foto |
| `cargo_tiene_voto_preferencial()` | Regla de dominio: senadores, diputados y parlamento andino tienen voto preferencial |

### Almacenamiento (`infrastructure/storage/r2_client.py`)

- Wrapper async sobre `boto3` (`asyncio.to_thread`) apuntando a Cloudflare R2
- Validaciones en cadena antes de cualquier upload:
  1. **Content-Type permitido**: `image/jpeg`, `image/png`, `image/webp`, `image/svg+xml`
  2. **Tamaño máximo**: `MAX_UPLOAD_BYTES = 5 MB` (exportado para uso en rutas)
  3. **Magic bytes**: verifica que el contenido real coincida con el Content-Type declarado (previene spoofing)
- Singleton `get_r2_adapter()` para reutilización de conexión

### Repositorios (`infrastructure/repositories/`)

| Archivo | Responsabilidad |
|---|---|
| `partido_repository.py` | CRUD de `partidos_politicos` |
| `proceso_repository.py` | CRUD de `procesos_electorales`, `listas_electorales`, `candidatos` |

### Servicios (`application/services/`)

| Servicio | Casos de uso |
|---|---|
| `PartidoService` | Crear partido (validando número y nombre únicos), listar, obtener, subir símbolo |
| `CedulaService` | Gestión completa de procesos, listas y candidatos; vista enriquecida de cédula |

**Vista de cédula enriquecida** (`CedulaView`):
- `PartidoResumen` — datos del partido (nombre, número, símbolo) embebidos en cada lista
- `ListaConPartido` — lista con partido ya resuelto; evita N+1 con `list_all()` en batch
- Candidatos ordenados: titulares primero (`not es_titular, orden`)

**Guards de seguridad en `CedulaService`**:
- IDOR en `add_candidato`: verifica que `lista.proceso_id == proceso_id`
- IDOR en `list_candidatos`: idem, cuando `proceso_id` es provisto

### Puertos (`application/ports.py`)

`StoragePort`, `PartidoRepositoryPort`, `ProcesoRepositoryPort` — contratos de interfaz para testabilidad e inversión de dependencias.

### Rutas HTTP (`api/v1/routes/`)

| Archivo | Prefijo | Endpoints |
|---|---|---|
| `partidos.py` | `/api/v1/partidos` | `POST /`, `GET /`, `GET /{id}`, `PATCH /{id}/simbolo` |
| `procesos.py` | `/api/v1/procesos` | `POST /`, `GET /`, `GET /{id}`, `PATCH /{id}/estado`, `POST /{id}/listas`, `GET /{id}/listas`, `POST /{id}/listas/{lid}/candidatos`, `GET /{id}/listas/{lid}/candidatos` |
| `candidatos.py` | `/api/v1/candidatos` | `PATCH /{id}/foto` |
| `cedula.py` | `/api/v1/cedula` | `GET /{proceso_id}` |

**Controles en rutas de upload** (partidos y candidatos):
- Lectura limitada: `file.read(MAX_UPLOAD_BYTES + 1)` → responde `413` antes de llamar al servicio
- Validación de magic bytes delegada al servicio/adaptador R2

### Migración de base de datos

`alembic/versions/20260504_0004_cedula_electoral.py`:
- Tablas: `partidos_politicos`, `procesos_electorales` (con `ARRAY(String)`), `listas_electorales`, `candidatos`
- Reversible con `downgrade()`

### Configuración (`.env` / `config.py`)

```
R2_ENDPOINT_URL=https://<ACCOUNT_ID>.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=election-assets
R2_PUBLIC_URL=https://assets.example.com
CORS_ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Otros cambios a infraestructura transversal

- `main.py`: `CORSMiddleware` + handler global `500` con `structlog`
- `core/exceptions.py`: `NotFoundError`, `StorageError`, `InvalidAssetError`

## Endpoints de la cédula — respuesta de ejemplo

`GET /api/v1/cedula/{proceso_id}`:

```json
{
  "proceso_id": "...",
  "nombre": "Elecciones Generales 2026",
  "fecha_jornada": "2026-06-06",
  "estado": "PUBLICADO",
  "tipos_cargo": ["PRESIDENTE_VICEPRESIDENTE"],
  "listas": [
    {
      "lista_id": "...",
      "partido": {
        "partido_id": "...",
        "nombre": "Fuerza Popular",
        "numero": 3,
        "simbolo_url": "https://assets.example.com/simbolos/.../logo.png"
      },
      "tipo_cargo": "PRESIDENTE_VICEPRESIDENTE",
      "tiene_voto_preferencial": false,
      "candidatos": [
        {"candidato_id": "...", "nombre_completo": "Keiko Fujimori", "orden": 1, "es_titular": true, "foto_url": null},
        {"candidato_id": "...", "nombre_completo": "Segundo Vicepresidente", "orden": 1, "es_titular": false, "foto_url": null}
      ]
    }
  ],
  "generated_at": "2026-05-04T14:00:00Z"
}
```

## Cobertura de tests

| Archivo | Tipo | Casos |
|---|---|---|
| `tests/test_cedula_domain.py` | Unitario (stubs en memoria) | 28 casos: reglas de dominio, magic bytes, `PartidoService`, `CedulaService` (procesos, listas, candidatos, IDOR, sort, vista cédula) |
| `tests/test_cedula_routes.py` | Integración HTTP (dependency override) | 28 casos: todos los endpoints, 413 en upload, 409 en duplicados, 404 en no encontrado, IDOR vía URL, estructura completa de respuesta cédula |

Total: 60 tests pasan (incluye los 4 pre-existentes). `ruff` y `mypy --strict` sin errores.

## TODO pendiente

- Autorización por permiso (`CEDULA_WRITE` / `CEDULA_READ`) en rutas de escritura — actualmente sin guard JWT
- Endpoint `PATCH /procesos/{id}/listas/{lid}` para editar partido/cargo de una lista existente
- Endpoint `DELETE /procesos/{id}/listas/{lid}/candidatos/{cid}` para remover candidato
- Paginación en `GET /procesos` y `GET /partidos`
- Query batch de candidatos en `get_cedula` (actualmente loop con queries individuales por lista)
