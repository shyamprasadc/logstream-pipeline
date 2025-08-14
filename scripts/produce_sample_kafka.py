from __future__ import annotations

import argparse
from kafka import KafkaProducer  # type: ignore
from app.config import settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: v.encode("utf-8"),
    )
    with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            producer.send(settings.kafka_topic, value=line)
    producer.flush()


if __name__ == "__main__":
    main()
