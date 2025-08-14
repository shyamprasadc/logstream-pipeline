from __future__ import annotations

from datetime import datetime, timedelta
from airflow import DAG  # type: ignore
from airflow.operators.python import PythonOperator  # type: ignore
import os

from app.ingestion.file_reader import read_lines
from app.parsing.parser import parse_line
from app.transformation.transformer import transform
from app.storage.postgres import init_db, insert_records
from app.storage.s3 import write_jsonl


def batch_task():
    init_db()
    path = os.getenv("SAMPLE_LOG_PATH", "/data/sample_logs/access.log")
    batch = []
    for line in read_lines(path):
        parsed = parse_line(line)
        if not parsed:
            continue
        batch.append(transform(parsed))
    if batch:
        insert_records(batch)
        try:
            write_jsonl(batch)
        except Exception:
            pass


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="batch_ingestion_dag",
    default_args=default_args,
    schedule_interval="@hourly",
    catchup=False,
    tags=["logs", "ingestion"],
) as dag:
    run_batch = PythonOperator(
        task_id="run_batch",
        python_callable=batch_task,
    )
