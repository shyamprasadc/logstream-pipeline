from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime
from typing import Optional

from app.storage.postgres import init_db, requests_per_endpoint, top_ips, error_rate
from app.logging_config import configure_logging
from app.config import settings

configure_logging("api")

app = FastAPI(title="Logstream Pipeline API")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    data = generate_latest()
    return PlainTextResponse(data, media_type=CONTENT_TYPE_LATEST)


@app.get("/analytics/requests_per_endpoint")
def api_requests_per_endpoint(
    start: Optional[str] = None, end: Optional[str] = None
) -> list:
    s = datetime.fromisoformat(start) if start else None
    e = datetime.fromisoformat(end) if end else None
    return requests_per_endpoint(s, e)


@app.get("/analytics/top_ips")
def api_top_ips(
    limit: int = 10, start: Optional[str] = None, end: Optional[str] = None
) -> list:
    s = datetime.fromisoformat(start) if start else None
    e = datetime.fromisoformat(end) if end else None
    return top_ips(limit=limit, start=s, end=e)


@app.get("/analytics/error_rate")
def api_error_rate(start: Optional[str] = None, end: Optional[str] = None) -> dict:
    s = datetime.fromisoformat(start) if start else None
    e = datetime.fromisoformat(end) if end else None
    return error_rate(s, e)
