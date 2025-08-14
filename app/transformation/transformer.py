from __future__ import annotations

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from user_agents import parse as parse_ua  # type: ignore
from app.config import settings

try:
    import geoip2.database  # type: ignore
except Exception:  # pragma: no cover - optional
    geoip2 = None  # type: ignore


def normalize_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    # fallback to now
    return datetime.now(timezone.utc)


def parse_user_agent(ua: Optional[str]) -> Dict[str, Optional[str]]:
    if not ua:
        return {"ua_device": None, "ua_os": None, "ua_browser": None}
    u = parse_ua(ua)
    return {
        "ua_device": "mobile"
        if u.is_mobile
        else "tablet"
        if u.is_tablet
        else "pc"
        if u.is_pc
        else None,
        "ua_os": str(u.os) if u.os else None,
        "ua_browser": str(u.browser) if u.browser else None,
    }


def enrich_geoip(ip: Optional[str]) -> Dict[str, Optional[str]]:
    if not settings.geoip_enabled or not ip:
        return {"country": None, "city": None}
    if geoip2 is None or not settings.geoip_db_path:
        return {"country": None, "city": None}
    try:
        reader = geoip2.database.Reader(settings.geoip_db_path)  # type: ignore
        resp = reader.city(ip)
        reader.close()
        country = resp.country.name
        city = resp.city.name
        return {"country": country, "city": city}
    except Exception:
        return {"country": None, "city": None}


def transform(record: Dict[str, Any]) -> Dict[str, Any]:
    record = dict(record)
    record["ts"] = normalize_timestamp(record.get("ts"))
    ua_info = parse_user_agent(record.get("user_agent"))
    record.update(ua_info)
    record.update(enrich_geoip(record.get("ip")))
    if record.get("response_time_ms") is not None:
        try:
            record["response_time_ms"] = int(record["response_time_ms"])  # type: ignore[index]
        except Exception:
            record["response_time_ms"] = None
    if record.get("status") is not None:
        try:
            record["status"] = int(record["status"])  # type: ignore[index]
        except Exception:
            record["status"] = None
    return record
