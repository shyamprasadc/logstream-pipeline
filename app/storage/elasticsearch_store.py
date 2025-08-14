from __future__ import annotations

from typing import Iterable, Dict, Any
from app.config import settings

try:
    from elasticsearch import Elasticsearch, helpers  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Elasticsearch = None  # type: ignore
    helpers = None  # type: ignore


def get_client():
    assert settings.enable_elasticsearch, "Elasticsearch disabled"
    assert Elasticsearch is not None, "elasticsearch package not installed"
    return Elasticsearch(settings.elasticsearch_host)


def bulk_index(records: Iterable[Dict[str, Any]]) -> None:
    if not settings.enable_elasticsearch:
        return
    client = get_client()
    actions = (
        {
            "_index": settings.elasticsearch_index,
            "_op_type": "index",
            "_source": r,
        }
        for r in records
    )
    helpers.bulk(client, actions)  # type: ignore
