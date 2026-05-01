---
description: "Use when changing SQLAlchemy models, Alembic files, or persistence contracts to keep schema and migrations consistent"
applyTo: "{src/election_system/infrastructure/db/**/*.py,alembic/**/*.py,alembic.ini}"
---

# Migrations Safety Rules

Use these rules for DB schema-related changes.

## Core rules

- Any persistent schema change must be represented by an Alembic migration.
- Keep ORM models and migration history consistent.
- Prefer additive, backward-compatible schema transitions.
- Do not silently rename or drop columns without an explicit migration step.

## PostgreSQL focus

- PostgreSQL is the primary DB; optimize decisions for Postgres behavior.
- Use explicit constraints for integrity-critical fields.
- Add indexes deliberately for high-cardinality or frequent-filter columns.

## Review checklist

1. Does every model change imply a migration update?
2. Are constraints/indexes explicitly handled?
3. Is rollback behavior considered?
4. Is the change aligned with [plans/04-modelo-datos-versionado-hash.md](../../plans/04-modelo-datos-versionado-hash.md)?
