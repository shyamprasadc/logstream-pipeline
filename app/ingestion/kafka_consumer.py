from __future__ import annotations

from typing import Iterator
from kafka import KafkaConsumer  # type: ignore
from app.config import settings


def get_consumer() -> KafkaConsumer:
    consumer = KafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: v.decode("utf-8", errors="ignore"),
        consumer_timeout_ms=1000,
    )
    return consumer


def stream_messages() -> Iterator[str]:
    consumer = get_consumer()
    for msg in consumer:
        yield msg.value  # already decoded utf-8
