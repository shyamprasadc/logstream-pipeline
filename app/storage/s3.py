from __future__ import annotations

from typing import Iterable
import json
import boto3
from botocore.config import Config
from datetime import datetime, timezone

from app.config import settings


def get_s3_client():
    session = boto3.session.Session()
    extra = {}
    if settings.s3_endpoint_url:
        extra["endpoint_url"] = settings.s3_endpoint_url
    if settings.s3_region:
        extra["region_name"] = settings.s3_region
    return session.client(
        "s3",
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        config=Config(s3={"addressing_style": "path"}, retries={"max_attempts": 3}),
        **extra,
    )


def write_jsonl(records: Iterable[dict]) -> str:
    # Writes a JSONL file to S3 and returns the key
    assert settings.s3_bucket, "S3 bucket must be configured"
    s3 = get_s3_client()
    now = datetime.now(timezone.utc)
    key = f"logs/year={now.year}/month={now.month:02d}/day={now.day:02d}/logs-{int(now.timestamp())}.jsonl"
    body = "\n".join(json.dumps(r, separators=(",", ":")) for r in records) + "\n"
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
    )
    return key
