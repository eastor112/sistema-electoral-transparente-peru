---
description: "Use when editing backend Python files to enforce api/application/domain/infrastructure boundaries"
applyTo: "src/election_system/**/*.py"
---

# Backend Layering Rules

Use these rules when modifying Python files under `src/election_system/`.

## Layer responsibilities

- `api/`: HTTP contracts, request/response mapping, dependency injection.
- `application/`: use cases and orchestration.
- `domain/`: pure business rules and invariants.
- `infrastructure/`: adapters for DB, messaging, storage, external services.
- `workers/`: async/event processing.

## Constraints

- Do not put domain rules in routers.
- Do not import infrastructure adapters into domain modules.
- Keep use cases in `application/` as the orchestration boundary.
- Keep endpoint handlers thin; delegate behavior to application services/use cases.
- Preserve TODO placeholders when a feature is intentionally scaffold-only.

## Edit quality checklist

1. Is logic placed in the correct layer?
2. Are imports directional (api -> application -> domain; infrastructure as adapter)?
3. Are auditability and traceability preserved in the changed flow?
4. Are changes aligned with [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)?
