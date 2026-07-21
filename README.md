# Great Energy Field — Phase 1 MVP

AI-guided wellness / energy-practice platform built around a **training-type AI Agent**
(knowledge base + user state + rules engine + training plan engine + AI generation).

See [development_plan.md](development_plan.md) for the full 6-week, two-milestone execution plan.

## Repository layout

```
backend/     FastAPI (Python) — Agent backend, API, DB (PostgreSQL + pgvector), Alembic
frontend/    Next.js + TypeScript + Tailwind — landing page + Founder/Admin dashboard
```

Each app has its **own** env file (`backend/.env`, `frontend/.env.local`) — copy from the
`.env.example` in each folder. Frontend and backend are **two deployables**: Next.js on Vercel,
FastAPI on a container host (Render / Railway / Fly.io), PostgreSQL on a managed provider
(Neon / Railway / RDS). The frontend calls the backend over HTTP with the FastAPI-issued JWT as a
bearer token. **No Supabase** — database and auth are handled entirely in FastAPI.

## Quick start

```bash
# Database (PostgreSQL + pgvector via Docker)
docker run --name gef-postgres -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=great_energy_field -p 5432:5432 \
  -d pgvector/pgvector:pg16

# Backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env                        # defaults point at the Docker Postgres above
uvicorn app.main:app --reload --port 8000   # http://localhost:8000/health

# Frontend (new terminal)
cd frontend && npm install
cp .env.example .env.local
npm run dev                                 # http://localhost:3000
```

Per-app details: [backend/README.md](backend/README.md) · [frontend/README.md](frontend/README.md).

## Status

Week 1 — Monday complete: repo structure, FastAPI skeleton (`/health`, settings, async SQLAlchemy,
Alembic, CORS), Next.js landing + `/admin` shell that reads live backend health. See the plan for
the day-by-day roadmap.
