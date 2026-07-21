"""FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import health

settings = get_settings()

app = FastAPI(
    title="Great Energy Field — Agent Backend",
    version="0.1.0",
    description="Phase 1 MVP FastAPI backend for the Great Energy Field training Agent.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"service": "great-energy-field-backend", "docs": "/docs"}
