## Logstream Pipeline

Production-grade Python data pipeline for web server logs with batch and real-time ingestion, parsing, transformation, storage, orchestration, API analytics, and monitoring.

### Features

#### ✅ Core Features (Fully Implemented)

- **Batch ingestion** from local files and **real-time streaming** via Kafka
- **Parsing** with `apachelogs` library and regex fallback for Apache/Nginx combined log format
- **Transformations**: timestamp normalization, user-agent parsing (device, OS, browser detection)
- **Storage**: PostgreSQL (querying), S3/MinIO (long-term JSON storage)
- **Orchestration**: Apache Airflow DAG for scheduled batch processing
- **API**: FastAPI analytics endpoints with Prometheus metrics
- **Monitoring**: Prometheus metrics collection and Grafana dashboard
- **Dockerized** with environment-driven configuration

#### 🔧 Optional Features (Partially Implemented)

- **GeoIP enrichment**: Requires manual GeoLite2 database download and configuration
- **Elasticsearch storage**: Implemented but not included in docker-compose (requires separate cluster)

### Prerequisites

- Docker + Docker Compose
- Optional: GeoLite2-City.mmdb for GeoIP enrichment

### Quickstart

1. Clone the repository
2. Start the stack:

```bash
docker compose up -d --build
```

3. Seed Kafka with sample logs (optional):

```bash
docker compose exec api python scripts/produce_sample_kafka.py --file /data/sample_logs/access.log
```

4. Access services:

- **API**: `http://localhost:8000/docs` - FastAPI analytics endpoints
- **Airflow**: `http://localhost:8080` (admin/admin) - Batch job orchestration
- **Prometheus**: `http://localhost:9090` - Metrics collection
- **Grafana**: `http://localhost:3000` (admin/admin) - Monitoring dashboard
- **Kafka UI**: `http://localhost:8081` - Kafka topic management
- **MinIO Console**: `http://localhost:9001` (minioadmin/minioadmin) - S3-compatible storage

### Project Structure

```
app/
  __init__.py
  config.py                    # Environment configuration
  logging_config.py            # Logging setup
  monitoring/
    metrics.py                 # Prometheus metrics
  ingestion/
    file_reader.py            # Batch file reading
    kafka_consumer.py         # Kafka streaming
  parsing/
    parser.py                 # Apache/Nginx log parsing
  transformation/
    transformer.py            # Data enrichment & normalization
  storage/
    postgres.py               # PostgreSQL operations
    s3.py                     # S3/MinIO storage
    elasticsearch_store.py    # Elasticsearch (optional)
api/
  main.py                     # FastAPI analytics endpoints
services/
  stream_consumer.py          # Kafka consumer service
airflow/
  dags/
    batch_ingestion_dag.py    # Scheduled batch processing
prometheus/
  prometheus.yml              # Metrics collection config
grafana/
  provisioning/
    datasources/
      datasource.yml          # Prometheus datasource
    dashboards/
      dashboards.yml          # Dashboard provisioning
  dashboards/
    pipeline_dashboard.json   # Monitoring dashboard
sample_data/
  sample_logs/
    access.log               # Sample Apache logs
scripts/
  ingest_file.py             # Manual batch ingestion
  produce_sample_kafka.py    # Kafka sample data producer
```

### Configuration

The application uses environment variables with sensible defaults. Key configurations:

- **Database**: PostgreSQL connection (auto-configured in docker-compose)
- **Kafka**: Bootstrap servers and topic configuration
- **S3/MinIO**: Storage endpoint and credentials
- **GeoIP**: Optional enrichment (disabled by default)

### Database Schema

Creates `web_logs` table in PostgreSQL with fields:

- `ip`, `ts`, `method`, `endpoint`, `status`, `response_time_ms`
- `user_agent`, `ua_device`, `ua_os`, `ua_browser`
- `country`, `city` (if GeoIP enabled)

### API Endpoints

- `GET /analytics/requests_per_endpoint` - Request counts by endpoint
- `GET /analytics/top_ips` - Top IP addresses by request count
- `GET /analytics/error_rate` - Error rate statistics
- `GET /metrics` - Prometheus metrics

### Airflow

- **DAG**: `batch_ingestion_dag` runs hourly
- **Task**: Reads from `SAMPLE_LOG_PATH` and loads into Postgres + S3
- **UI**: Access at `http://localhost:8080` (admin/admin)

### Monitoring

- **Prometheus**: Scrapes metrics from API (`/metrics`) and Consumer (`:8001/metrics`)
- **Grafana**: Auto-loads dashboard with processing metrics
- **Metrics**: Records processed, errors, and latency

### Optional Features Setup

#### GeoIP Enrichment

1. Download GeoLite2-City.mmdb from MaxMind
2. Mount to `/data/GeoLite2-City.mmdb` in containers
3. Set `GEOIP_ENABLED=true` in environment

#### Elasticsearch

1. Add Elasticsearch service to docker-compose
2. Set `ENABLE_ELASTICSEARCH=true` in environment
3. Configure `ELASTICSEARCH_HOST` and `ELASTICSEARCH_INDEX`

### Development

- API hot-reloads when mounting the repository
- Consumer includes embedded metrics server
- All services use structured logging

### Cleanup

```bash
docker compose down -v
```

### Troubleshooting

- **Kafka connection issues**: Wait for Kafka to fully start (health checks in place)
- **Database connection**: PostgreSQL health checks ensure readiness
- **S3/MinIO**: Bucket creation is automatic via init container
- **Metrics not showing**: Check Prometheus targets at `http://localhost:9090/targets`
