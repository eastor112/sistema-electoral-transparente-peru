# Senior Architecture Blueprint

## Goals

- Clean separation of concerns by layers.
- Strong auditability and traceability.
- Horizontal scalability and offline-first operation.
- Extensibility for future electoral features.

## Layered structure

- api: HTTP contracts, request/response validation, auth boundaries.
- application: use cases, orchestration, transaction boundaries.
- domain: entities, invariants, pure business rules.
- infrastructure: database, messaging, storage, integrations.
- workers: asynchronous processing and projections.

## Bounded modules (planned)

- mesas: attendance, replacement, opening/closing lifecycle.
- actas: capture, signatures, publication, versioning.
- incidencias: reports, evidence, public summaries.
- fiabilidad: scoring 1-10 and factors.
- auditoria: immutable logs and validator-facing events.

## Cross-cutting concerns

- structured logging and tracing.
- idempotency and sequence guarantees.
- role-based and attribute-based access control.
- offline synchronization integrity.

## Non-functional guardrails

- stateless APIs behind load balancer.
- queue-backed asynchronous workloads.
- projection rebuild from event history.
- failure isolation per module.
