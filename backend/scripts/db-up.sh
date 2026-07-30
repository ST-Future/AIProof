#!/usr/bin/env bash
# Recreate the local dev database and bring it to a ready state in one step:
# fresh Postgres+pgvector container, migrations, seed data, and a founder admin.
#
# Usage (from the backend/ directory, with the venv active):
#   ./scripts/db-up.sh
#
# Env overrides: PG_PORT (default 5434), ADMIN_EMAIL, ADMIN_PASSWORD.
set -euo pipefail

PG_PORT="${PG_PORT:-5434}"
ADMIN_EMAIL="${ADMIN_EMAIL:-founder@greatenergyfield.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-Founder1234}"

echo "==> Recreating Postgres container (port ${PG_PORT})"
docker rm -f gef-postgres >/dev/null 2>&1 || true
docker run --name gef-postgres \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=great_energy_field \
  -p "${PG_PORT}:5432" -d pgvector/pgvector:pg16 >/dev/null

echo "==> Waiting for Postgres to accept connections"
until docker exec gef-postgres pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done
sleep 1

echo "==> Applying migrations"
alembic upgrade head >/dev/null

echo "==> Seeding reference data"
python -m app.seed | tail -1

echo "==> Creating founder admin (${ADMIN_EMAIL})"
python -m app.create_admin "${ADMIN_EMAIL}" "${ADMIN_PASSWORD}" Founder | tail -1

echo "==> Done. Backend can start:  uvicorn app.main:app --reload --port 8000"
