# AGENTS.md

This file provides repository-specific guidance for AI coding agents working in this project.

## Scope

- Applies to the whole repository.
- Prioritize minimal, safe, and traceable changes.
- Preserve the current layered architecture and offline-first/audit-first direction.

## Project Context

- Backend stack: FastAPI + PostgreSQL + Redis.
- Source layout uses `src/` (package: `election_system`).
- Current codebase is scaffold-first: many endpoints/services are placeholders with TODOs by design.

## Runbook Commands

- Create env: `python3 -m venv .venv`
- Install runtime deps: `make install`
- Install dev deps: `make install-dev`
- Run API: `make run`
- Tests: `make test`
- Lint: `make lint`
- Typecheck: `make typecheck`

Note: commands already set `PYTHONPATH=src` in [Makefile](Makefile).

## Architecture Boundaries

- `src/election_system/api`: HTTP layer only (routers/dependencies/contracts).
- `src/election_system/application`: use cases and orchestration.
- `src/election_system/domain`: entities and business invariants.
- `src/election_system/infrastructure`: DB/adapters/integrations.
- `src/election_system/workers`: async/event workloads.

Do not move business logic into routers; keep orchestration in application layer and rules in domain.

## Database and Migrations

- Primary DB is PostgreSQL.
- SQLAlchemy + Alembic are scaffolded.
- Alembic env is configured for `src/` layout.
- Add migrations for schema changes; avoid implicit schema drift.

## Coding Conventions

- Python 3.12.
- Strict typing is enabled in [pyproject.toml](pyproject.toml) (`mypy strict = true`).
- Ruff is the linter/formatter gate.
- Respect [/.editorconfig](.editorconfig).
- Keep TODO placeholders explicit when a feature is intentionally not implemented.

## Existing Documentation (Link, Don’t Duplicate)

- Product and transparency context: [README.md](README.md)
- High-level architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Implementation backlog: [docs/TODO.md](docs/TODO.md)
- Detailed electoral system plans: [plans/02-arquitectura-backend-python.md](plans/02-arquitectura-backend-python.md)

## Pitfalls and Guardrails

- This repository is sensitive (elections): favor explicitness, auditability, and reversible changes.
- Avoid “quick fixes” that bypass logging, traceability, or role/permission boundaries.
- Do not implement speculative business behavior not reflected in plans/docs.
- Keep public API behavior stable unless the task explicitly requests breaking changes.

## Preferred Change Pattern

1. Read the nearest owning layer.
2. Apply small patch.
3. Run the narrowest validation command.
4. Report exactly what changed and what remains TODO.
