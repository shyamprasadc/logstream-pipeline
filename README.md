## Logstream Pipeline

Production-grade Python data pipeline for web server logs with batch and real-time ingestion, parsing, transformation, storage, orchestration, API analytics, and monitoring.

### Features

- Batch ingestion from local files and real-time streaming via Kafka
- Parsing with `apachelogs` or regex fallback
- Transformations: timestamp normalization, user-agent parsing, optional GeoIP enrichment
- Storage: PostgreSQL (querying), S3/MinIO (long-term JSON storage), optional Elasticsearch
- Orchestration: Apache Airflow (DAG for batch processing)
- API: FastAPI analytics endpoints
- Monitoring: Prometheus metrics and Grafana dashboard
- Dockerized with environment-driven configuration

### Prerequisites

- Docker + Docker Compose

### Quickstart

1. Clone repo and use provided `.env`.
2. Start the stack:

```bash
docker compose up -d --build
```

3. Seed Kafka with sample logs (optional):

```bash
docker compose exec api python scripts/produce_sample_kafka.py --file /data/sample_logs/access.log
```

4. Access services:

- API: `http://localhost:8000/docs`
- Airflow: `http://localhost:8080` (admin/admin)
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (admin/admin)
- Kafka UI: `http://localhost:8081`
- MinIO Console: `http://localhost:9001` (minioadmin/minioadmin)

### Project Structure

```
app/
  __init__.py
  config.py
  logging_config.py
  monitoring/
    metrics.py
  ingestion/
    file_reader.py
    kafka_consumer.py
  parsing/
    parser.py
  transformation/
    transformer.py
  storage/
    postgres.py
    s3.py
    elasticsearch_store.py
api/
  main.py
services/
  stream_consumer.py
airflow/
  dags/
    batch_ingestion_dag.py
prometheus/
  prometheus.yml
grafana/
  provisioning/
    datasources/
      datasource.yml
    dashboards/
      dashboards.yml
  dashboards/
    pipeline_dashboard.json
sample_data/
  sample_logs/
    access.log
scripts/
  ingest_file.py
  produce_sample_kafka.py
```

### Environment

See `.env` for configurable values. The stack uses MinIO as an S3-compatible backend.

### Database

Creates `web_logs` table in PostgreSQL. Analytics endpoints query this table.

### Airflow

- DAG `batch_ingestion_dag` reads from `SAMPLE_LOG_PATH` and loads into Postgres and S3.
- UI at `http://localhost:8080` (admin/admin).

### Prometheus & Grafana

- Prometheus scrapes API and consumer metrics endpoints.
- Grafana auto-loads `pipeline_dashboard.json`.

### Cleanup

```bash
docker compose down -v
```
