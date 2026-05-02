# Roles y permisos (RBAC + ABAC)

Fecha: 2026-05-02
Estado: completado

## Resumen

Se implemento el sistema de roles y permisos del sistema electoral basado en RBAC estatico con
restriccion de ambito ABAC. Permite asignar roles con contexto operacional (mesa, ubigeo, jornada)
e integra la verificacion de permisos directamente en el pipeline de autenticacion de FastAPI.

Fuente de diseno: `plans/09-panel-administracion-roles-y-cedula.md`, seccion 3.

## Roles del sistema

| RoleType                 | Descripcion |
|--------------------------|-------------|
| `ADMIN_NACIONAL`         | Acceso total. Configura catalogos globales y politicas. |
| `ADMIN_REGIONAL`         | Configura mesas y asignaciones dentro de su ambito de ubigeo. |
| `MIEMBRO_MESA_TITULAR`   | Presidente, secretario o tercer miembro. Opera su mesa asignada. |
| `MIEMBRO_MESA_SUPLENTE`  | Opera solo cuando el sistema registra su activacion por ausencia. |
| `ELECTOR_AD_HOC`         | Designado excepcionalmente; opera solo tras designacion auditada. |
| `FISCALIZADOR`           | ONPE/JNE. Acceso de observacion y validacion. |
| `PERSONERO`              | Observacion + reporte de incidencias. |
| `ELECTOR`                | Solo lectura de datos publicos de mesa e incidencias. |

## Permisos granulares

| Permission          | Area |
|---------------------|------|
| `MESA_READ`         | Mesas |
| `MESA_WRITE`        | Mesas |
| `MESA_ASSIGN`       | Mesas |
| `ACTOR_READ`        | Actores/usuarios |
| `ACTOR_WRITE`       | Actores/usuarios |
| `ACTOR_ASSIGN_ROLE` | Actores/usuarios |
| `ACTA_READ`         | Actas |
| `ACTA_WRITE`        | Actas |
| `ACTA_SIGN`         | Actas |
| `CEDULA_READ`       | Cedula electoral |
| `CEDULA_WRITE`      | Cedula electoral |
| `CEDULA_FREEZE`     | Cedula electoral |
| `JORNADA_OPEN`      | Jornada |
| `JORNADA_CLOSE`     | Jornada |
| `INCIDENCIA_READ`   | Incidencias |
| `INCIDENCIA_WRITE`  | Incidencias |
| `ADMIN_PANEL`       | Panel de administracion |
| `PUBLIC_READ`       | Datos publicos ciudadanos |

Los permisos por rol se definen en `ROLE_PERMISSIONS` en `domain/models.py`. El catalogo es
estatico y no es modificable en tiempo de ejecucion (inmutable via `frozenset`).

## Ambito ABAC

Cada asignacion de rol puede restringirse a un contexto especifico mediante atributos opcionales:

- `mesa_id`: restringe operacion a una mesa concreta.
- `ubigeo`: restringe operacion a un ambito geografico.
- `jornada_id`: restringe operacion a una jornada electoral especifica.

`None` en todos ellos equivale a ambito global.

La capa de aplicacion/dominio es responsable de validar estos atributos en operaciones criticas;
el sistema de permisos actual aplica el RBAC base. La validacion de ambito ABAC por operacion
queda pendiente a medida que se implementen los modulos de actas, mesas y jornadas.

## Flujo de autenticacion actualizado

Con esta feature, cada request autenticado:

1. Valida el Bearer JWT (access token).
2. Carga los roles activos del actor desde la tabla `user_roles` via `RoleRepository`.
3. Retorna un `CurrentActor` con `actor_id`, `roles`, `permissions` y helpers de verificacion.

Dependencias disponibles para rutas:

```python
# Requiere al menos uno de los roles indicados
require_roles(RoleType.ADMIN_NACIONAL, RoleType.ADMIN_REGIONAL)

# Requiere TODOS los permisos indicados
require_permissions(Permission.MESA_WRITE, Permission.ACTA_READ)
```

## API de gestion de roles

Todas las rutas requieren rol `ADMIN_NACIONAL`.

| Metodo   | Ruta                             | Descripcion |
|----------|----------------------------------|-------------|
| `POST`   | `/api/v1/roles`                  | Asignar rol a usuario |
| `DELETE` | `/api/v1/roles/{user_role_id}`   | Revocar asignacion activa |
| `GET`    | `/api/v1/roles`                  | Listar asignaciones con filtros |
| `GET`    | `/api/v1/roles/users/{user_id}`  | Roles activos de un usuario |
| `GET`    | `/api/v1/roles/catalog/permissions` | Catalogo de permisos por rol |

### Filtros disponibles en `GET /roles`

- `user_id` (str, opcional)
- `role_type` (RoleType, opcional)
- `is_active` (bool, default `true`)
- `limit` (1-200, default 50)
- `offset` (default 0)

### Regla de duplicados

No se permite asignar el mismo rol con identico ambito `(mesa_id, ubigeo, jornada_id)` a un
usuario si ya tiene una asignacion activa con esos valores. Genera `409 Conflict`.

## Modelo de datos

Migracion: `20260502_0003_user_roles.py`

Tabla `user_roles`:

| Columna        | Tipo          | Notas |
|----------------|---------------|-------|
| `user_role_id` | `VARCHAR(36)` | PK, UUID |
| `user_id`      | `VARCHAR(36)` | FK → `users.user_id` ON DELETE CASCADE |
| `role_type`    | `VARCHAR(32)` | Valor de `RoleType` |
| `mesa_id`      | `VARCHAR(50)` | Nullable, ambito ABAC |
| `ubigeo`       | `VARCHAR(6)`  | Nullable, ambito ABAC |
| `jornada_id`   | `VARCHAR(36)` | Nullable, ambito ABAC |
| `is_active`    | `BOOLEAN`     | Soft-delete logico |
| `assigned_by`  | `VARCHAR(36)` | FK → `users.user_id` ON DELETE RESTRICT |
| `assigned_at`  | `TIMESTAMPTZ` | Trazabilidad de asignacion |
| `revoked_at`   | `TIMESTAMPTZ` | Nullable; registrado al revocar |

`assigned_by` usa `ON DELETE RESTRICT` para preservar la trazabilidad audit-first: no se puede
eliminar un admin que tenga asignaciones registradas.

## Seguridad y controles

- Los roles se cargan en cada request autenticado; no se cachean en el token JWT (resistente a revocacion inmediata).
- La revocacion es logica (`is_active=False`, `revoked_at` registrado) — nunca se borran filas.
- `ConflictError` fue corregido para extender `DomainError` directamente (no `AuthError`), ya que aplica a conflictos genericos de dominio.
- El `assigned_by` tiene FK referencial hacia `users` para garantizar integridad de la cadena de custodia.

## Archivos principales

- `src/election_system/domain/models.py` — `RoleType`, `Permission`, `ROLE_PERMISSIONS`, `UserRole`
- `src/election_system/application/ports.py` — `RoleRepositoryPort`
- `src/election_system/application/services/role_service.py` — `RoleService`
- `src/election_system/api/dependencies/auth.py` — `CurrentActor`, `get_current_actor`, `require_roles`, `require_permissions`
- `src/election_system/api/v1/routes/roles.py` — rutas de gestion
- `src/election_system/infrastructure/db/models.py` — `UserRoleORM`
- `src/election_system/infrastructure/repositories/role_repository.py` — `RoleRepository`
- `alembic/versions/20260502_0003_user_roles.py`

## Validacion ejecutada

- `make lint` — sin errores
- `make typecheck` — 46 archivos sin issues (mypy strict)
- `make test` — 4 passed

## Pendientes relacionados

- Validacion de ambito ABAC por operacion (se implementa al desarrollar actas, mesas y jornadas).
- Activacion condicional de suplentes y electores ad hoc segun estado de jornada.
- Auditoria de intentos con permiso denegado (eventos inmutables, plan 09 seccion 4).
