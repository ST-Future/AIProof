# Great Energy Field — Backend (FastAPI)

Phase 1 MVP Agent backend. Python 3.11+, FastAPI, async SQLAlchemy 2.0, Alembic, PostgreSQL + pgvector. Auth is FastAPI-native (no external provider).

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # defaults target a local Postgres; edit DATABASE_URL as needed
```

## Database (local, Docker)

```bash
docker run --name gef-postgres -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=great_energy_field -p 5432:5432 -d pgvector/pgvector:pg16
```

The `pgvector/pgvector` image is stock Postgres with the `vector` extension available
(`CREATE EXTENSION vector;` is applied by the Week 1 migration).

> **Port already in use?** If host port `5432` is taken (e.g. a local Postgres is running),
> map a different host port — e.g. `-p 5434:5432` — and update `DATABASE_URL` /
> `DATABASE_URL_SYNC` in `backend/.env` to match.

## Run

```bash
uvicorn app.main:app --reload --port 8000
# API docs:   http://localhost:8000/docs
# Health:     http://localhost:8000/health
```

## Migrations (Alembic)

```bash
alembic revision --autogenerate -m "message"   # create migration from models
alembic upgrade head                            # apply migrations
alembic downgrade -1                            # roll back one
```

Alembic reads `DATABASE_URL_SYNC` (sync driver) from settings; the app uses `DATABASE_URL` (async).

## Seed reference data

```bash
python -m app.seed   # training stages, default system prompt, safety risk rules (idempotent)
```

## Quality

```bash
ruff check .        # lint
black .             # format
mypy app            # type-check
pytest              # tests
```

## Layout

```
app/
  main.py        # FastAPI app + CORS + router registration
  config.py      # Pydantic settings (env)
  db.py          # async engine, session, DeclarativeBase
  routers/       # API routers (health, later: chat, training, admin, payments)
  models/        # SQLAlchemy models (Alembic target_metadata)
  schemas/       # Pydantic request/response models
  services/      # business logic (rules engine, RAG, agent runtime)
migrations/      # Alembic
tests/
```
