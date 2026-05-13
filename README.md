# Sistema Electoral Digital Auditado

Backend en Python para un sistema electoral auditable, transparente y resiliente. Orientado a eliminar cajas negras en procesos críticos para la democracia.

> **Principio rector:** confiar en reglas verificables, no en operadores individuales.

---

## ¿Por qué existe este proyecto?

Ante cuestionamientos e irregularidades documentadas en las últimas elecciones en el Perú, este proyecto propone una alternativa técnica que sea:

- Verificable por terceros (auditores, academia, ciudadanía).
- Trazable de extremo a extremo, sin posibilidad de edición silenciosa.
- Resiliente ante conectividad intermitente (offline-first).
- Escalable para soportar una jornada electoral nacional completa.

---

## Stack

| Capa | Tecnología |
|---|---|
| API | Python 3.12 · FastAPI · Uvicorn |
| Base de datos | PostgreSQL 16 |
| Caché / colas | Redis |
| Storage de actas | Object Storage S3-compatible (Cloudflare R2) |
| Mensajería | NATS / Kafka |
| Observabilidad | OpenTelemetry · Prometheus · Grafana · Loki |

---

## Inicio rápido

```bash
python3 -m venv .venv && source .venv/bin/activate
make install-dev   # instala dependencias de desarrollo
make run           # levanta la API en http://localhost:8000
```

Otros comandos:

```bash
make test       # ejecuta tests
make lint       # linter (ruff)
make typecheck  # tipado estático (mypy strict)
make hooks      # activa pre-push hook (test + lint + typecheck)
```

---

## Arquitectura

```
src/election_system/
├── api/            # Routers, dependencias, contratos HTTP
├── application/    # Casos de uso y orquestación
├── domain/         # Entidades y reglas de negocio
├── infrastructure/ # DB, storage, notificaciones, repositorios
└── workers/        # Tareas asíncronas y procesamiento de eventos
```

Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para el diseño detallado.

---

## Flujo operativo

| Fase | Descripción |
|---|---|
| Pre-jornada | Configuración de mesas, candidatos, cédula y asignación de roles |
| Jornada | Operación offline-first por mesa; sincronización automática al recuperar conectividad |
| Cierre | Firma de declaración jurada por miembros, personeros y fiscalizadores |
| Post-jornada | Publicación inmediata, auditoría distribuida y calificación de fiabilidad por mesa |

Cuando un acta queda validada: se persiste, se contabiliza, se emite al bus de eventos y se publica su trazabilidad — sin pasos manuales intermedios.

---

## Documentación

| Documento | Contenido |
|---|---|
| [plans/01-vision-y-principios.md](plans/01-vision-y-principios.md) | Visión y principios de diseño |
| [plans/02-arquitectura-backend-python.md](plans/02-arquitectura-backend-python.md) | Arquitectura técnica y decisiones clave |
| [plans/03-seguridad-identidad-criptografia.md](plans/03-seguridad-identidad-criptografia.md) | Autenticación, firmas digitales y modelo de confianza |
| [plans/04-modelo-datos-versionado-hash.md](plans/04-modelo-datos-versionado-hash.md) | Modelo de datos, versionado y log inmutable |
| [plans/05-flujo-operativo-estados-acta.md](plans/05-flujo-operativo-estados-acta.md) | Máquina de estados y reglas de negocio del acta |
| [plans/06-validadores-distribucion-auditoria.md](plans/06-validadores-distribucion-auditoria.md) | Nodos validadores, broadcast y detección de anomalías |
| [plans/07-operacion-devsecops-observabilidad.md](plans/07-operacion-devsecops-observabilidad.md) | Despliegue, observabilidad y seguridad operacional |
| [plans/08-roadmap-riesgos-gobernanza.md](plans/08-roadmap-riesgos-gobernanza.md) | Roadmap, riesgos y gobernanza |
| [plans/09-panel-administracion-roles-y-cedula.md](plans/09-panel-administracion-roles-y-cedula.md) | Panel de administración, roles y diseño de cédula |
| [docs/TODO.md](docs/TODO.md) | Backlog de implementación |

---

## Contribuir

Se buscan aportes de ingenieros, auditores, especialistas electorales y organizaciones civiles. Toda contribución debe fortalecer al menos uno de estos atributos: **transparencia · auditabilidad · resiliencia · integridad · usabilidad · escalabilidad**.
