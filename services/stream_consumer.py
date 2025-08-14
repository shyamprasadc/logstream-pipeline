from __future__ import annotations

import time
from typing import List, Dict, Any
import logging

from app.ingestion.kafka_consumer import stream_messages
from app.parsing.parser import parse_line
from app.transformation.transformer import transform
from app.storage.postgres import init_db, insert_records
from app.storage.s3 import write_jsonl
from app.storage.elasticsearch_store import bulk_index
from app.monitoring.metrics import (
    processed_records_total,
    processing_errors_total,
    processing_latency_seconds,
)
from app.logging_config import configure_logging
from app.config import settings

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import uvicorn

configure_logging("consumer")
logger = logging.getLogger(__name__)

app = FastAPI(title="Logstream Consumer Metrics")


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    data = generate_latest()
    return PlainTextResponse(data, media_type=CONTENT_TYPE_LATEST)


def process_batch(batch: List[Dict[str, Any]]) -> None:
    if not batch:
        return
    insert_records(batch)
    try:
        write_jsonl(batch)
    except Exception as e:
        logger.warning("S3 write failed: %s", e)
    try:
        bulk_index(batch)
    except Exception:
        pass


def run_consumer_loop() -> None:
    init_db()
    batch: List[Dict[str, Any]] = []
    last_flush = time.time()
    batch_size = settings.consumer_s3_batch_size
    batch_seconds = settings.consumer_s3_batch_seconds

    for msg in stream_messages():
        start = time.time()
        try:
            parsed = parse_line(msg)
            if not parsed:
                continue
            rec = transform(parsed)
            batch.append(rec)
            processed_records_total.inc()
        except Exception:
            processing_errors_total.inc()
            continue
        finally:
            processing_latency_seconds.observe(time.time() - start)

        if len(batch) >= batch_size or (time.time() - last_flush) >= batch_seconds:
            process_batch(batch)
            batch = []
            last_flush = time.time()


if __name__ == "__main__":
    # Run metrics HTTP server alongside consumer
    import threading

    def start_http():
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

    t = threading.Thread(target=start_http, daemon=True)
    t.start()

    run_consumer_loop()
