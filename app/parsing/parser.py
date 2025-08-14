from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime, timezone
import re

try:
    from apachelogs import LogParser  # type: ignore
except Exception:  # pragma: no cover - optional
    LogParser = None  # type: ignore

COMMON_FORMAT = '%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"'

# Regex fallback for common/combined log format with response time at end if present
LOG_REGEX = re.compile(
    r"^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] \"(?P<method>\S+) (?P<endpoint>\S+) \S+\" (?P<status>\d{3}) \S+ \"[^\"]*\" \"(?P<ua>[^\"]*)\"(?: (?P<rt>\d+))?$"
)


def parse_apache_time(ts: str) -> datetime:
    # Example: 10/Oct/2000:13:55:36 -0700
    dt = datetime.strptime(ts, "%d/%b/%Y:%H:%M:%S %z")
    return dt.astimezone(timezone.utc)


def parse_line(line: str) -> Optional[Dict[str, Any]]:
    # Try apachelogs if available
    if LogParser is not None:
        try:
            parser = LogParser(COMMON_FORMAT)
            e = parser.parse(line)
            method = None
            endpoint = None
            if e.request_line:
                parts = e.request_line.split()
                if len(parts) >= 2:
                    method = parts[0]
                    endpoint = parts[1]
            return {
                "ip": e.remote_host or "",
                "ts": e.request_time_fields[0]
                if getattr(e, "request_time_fields", None)
                else e.request_time,
                "method": method,
                "endpoint": endpoint,
                "status": int(e.final_status) if e.final_status else None,
                "response_time_ms": None,
                "user_agent": e.headers_in.get("User-Agent", "")
                if getattr(e, "headers_in", None)
                else "",
            }
        except Exception:
            pass

    # Regex fallback
    m = LOG_REGEX.match(line)
    if not m:
        return None
    groups = m.groupdict()
    ts = parse_apache_time(groups["time"])  # type: ignore[arg-type]
    rt = groups.get("rt")
    return {
        "ip": groups.get("ip", ""),
        "ts": ts,
        "method": groups.get("method"),
        "endpoint": groups.get("endpoint"),
        "status": int(groups.get("status")) if groups.get("status") else None,
        "response_time_ms": int(rt) if rt else None,
        "user_agent": groups.get("ua"),
    }
