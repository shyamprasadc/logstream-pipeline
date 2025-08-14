from __future__ import annotations

from typing import Iterable, List, Dict, Any, Optional
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    MetaData,
    DateTime,
    Text,
    Index,
)
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text
from datetime import datetime

from app.config import settings


metadata = MetaData()

web_logs = Table(
    "web_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("ip", String(64), nullable=False),
    Column("ts", DateTime(timezone=True), nullable=False),
    Column("method", String(16), nullable=True),
    Column("endpoint", Text, nullable=True),
    Column("status", Integer, nullable=True),
    Column("response_time_ms", Integer, nullable=True),
    Column("user_agent", Text, nullable=True),
    Column("ua_device", String(64), nullable=True),
    Column("ua_os", String(128), nullable=True),
    Column("ua_browser", String(128), nullable=True),
    Column("country", String(128), nullable=True),
    Column("city", String(128), nullable=True),
)

Index("idx_weblogs_ts", web_logs.c.ts)
Index("idx_weblogs_endpoint", web_logs.c.endpoint)
Index("idx_weblogs_status", web_logs.c.status)

_engine: Optional[Engine] = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.sqlalchemy_url, pool_pre_ping=True, future=True
        )
    return _engine


def init_db() -> None:
    engine = get_engine()
    metadata.create_all(engine)


def insert_records(records: Iterable[Dict[str, Any]]) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(web_logs.insert(), list(records))


# Analytics queries


def requests_per_endpoint(
    start: Optional[datetime] = None, end: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    engine = get_engine()
    query = "SELECT endpoint, COUNT(*) as count FROM web_logs WHERE 1=1"
    params: Dict[str, Any] = {}
    if start is not None:
        query += " AND ts >= :start"
        params["start"] = start
    if end is not None:
        query += " AND ts <= :end"
        params["end"] = end
    query += " GROUP BY endpoint ORDER BY count DESC"
    with engine.begin() as conn:
        rows = conn.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


def top_ips(
    limit: int = 10, start: Optional[datetime] = None, end: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    engine = get_engine()
    query = "SELECT ip, COUNT(*) as count FROM web_logs WHERE 1=1"
    params: Dict[str, Any] = {}
    if start is not None:
        query += " AND ts >= :start"
        params["start"] = start
    if end is not None:
        query += " AND ts <= :end"
        params["end"] = end
    query += " GROUP BY ip ORDER BY count DESC LIMIT :limit"
    params["limit"] = limit
    with engine.begin() as conn:
        rows = conn.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


def error_rate(
    start: Optional[datetime] = None, end: Optional[datetime] = None
) -> Dict[str, Any]:
    engine = get_engine()
    base = "FROM web_logs WHERE 1=1"
    params: Dict[str, Any] = {}
    if start is not None:
        base += " AND ts >= :start"
        params["start"] = start
    if end is not None:
        base += " AND ts <= :end"
        params["end"] = end

    with engine.begin() as conn:
        total = conn.execute(text(f"SELECT COUNT(*) {base}"), params).scalar() or 0
        errors = (
            conn.execute(
                text(f"SELECT COUNT(*) {base} AND status >= 500"), params
            ).scalar()
            or 0
        )
    rate = (errors / total) if total else 0.0
    return {"total": int(total), "errors": int(errors), "error_rate": rate}
