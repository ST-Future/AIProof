# Great Energy Field — Frontend (Next.js)

Phase 1 MVP client. Next.js (App Router) + React + TypeScript + Tailwind CSS. Talks to the FastAPI backend over HTTP.

## Setup

```bash
cd frontend
npm install
cp .env.example .env.local   # point the app at the backend (NEXT_PUBLIC_API_BASE_URL)
```

## Run

```bash
npm run dev     # http://localhost:3000  (landing)  /  /admin (dashboard shell)
npm run build   # production build
npm run lint    # eslint
```

## Notes

- `src/lib/api.ts` — thin backend client (`API_BASE_URL`, `getHealth`, `apiGet`). All future
  `/api/*` calls go through here with the FastAPI-issued JWT as a bearer token.
- `/admin` renders the Founder/Admin shell and live backend health via `BackendStatus`.
