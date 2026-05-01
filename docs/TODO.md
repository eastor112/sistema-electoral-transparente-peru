# TODO Backlog

## API

- [ ] Implement request/response schemas for admin and mesas endpoints.
- [ ] Add exception handlers and error catalog.
- [ ] Add authentication and authorization dependencies.

## Application

- [ ] Implement full use cases for apertura, incidencias, declaracion jurada.
- [ ] Add transaction scripts and idempotency checks.
- [ ] Add reliability scoring pipeline (1-10) with weighted factors.

## Domain

- [ ] Define full electoral invariants and state transitions.
- [ ] Add replacement policy rules (titular/suplente/ad-hoc).

## Infrastructure

- [ ] Add Alembic migrations and seed strategy.
- [ ] Add repositories for actas, incidencias, auditoria.
- [ ] Add message bus adapters and outbox implementation.

## Operations

- [ ] Add CI workflow with lint/test/typecheck.
- [ ] Add deployment manifests for staging and production.
- [ ] Add runbooks for offline sync and incident response.
