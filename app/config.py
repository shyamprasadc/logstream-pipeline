from pydantic import BaseModel
from pydantic import Field
from pydantic import computed_field
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    env: str = Field(default=os.getenv("ENV", "local"))

    # Postgres
    postgres_host: str = Field(default=os.getenv("POSTGRES_HOST", "localhost"))
    postgres_port: int = Field(default=int(os.getenv("POSTGRES_PORT", 5432)))
    postgres_db: str = Field(default=os.getenv("POSTGRES_DB", "logs"))
    postgres_user: str = Field(default=os.getenv("POSTGRES_USER", "loguser"))
    postgres_password: str = Field(default=os.getenv("POSTGRES_PASSWORD", "logpass"))

    # Kafka
    kafka_bootstrap_servers: str = Field(
        default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    )
    kafka_topic: str = Field(default=os.getenv("KAFKA_TOPIC", "webserver-logs"))
    kafka_group_id: str = Field(
        default=os.getenv("KAFKA_GROUP_ID", "log-consumer-group")
    )

    # S3
    s3_endpoint_url: Optional[str] = Field(default=os.getenv("S3_ENDPOINT_URL"))
    s3_access_key: Optional[str] = Field(default=os.getenv("S3_ACCESS_KEY"))
    s3_secret_key: Optional[str] = Field(default=os.getenv("S3_SECRET_KEY"))
    s3_region: Optional[str] = Field(default=os.getenv("S3_REGION"))
    s3_bucket: Optional[str] = Field(default=os.getenv("S3_BUCKET"))
    s3_use_ssl: bool = Field(default=os.getenv("S3_USE_SSL", "false").lower() == "true")

    # Elasticsearch (optional)
    enable_elasticsearch: bool = Field(
        default=os.getenv("ENABLE_ELASTICSEARCH", "false").lower() == "true"
    )
    elasticsearch_host: str = Field(
        default=os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
    )
    elasticsearch_index: str = Field(
        default=os.getenv("ELASTICSEARCH_INDEX", "web-logs")
    )

    # GeoIP (optional)
    geoip_enabled: bool = Field(
        default=os.getenv("GEOIP_ENABLED", "false").lower() == "true"
    )
    geoip_db_path: Optional[str] = Field(default=os.getenv("GEOIP_DB_PATH"))

    # API
    api_host: str = Field(default=os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = Field(default=int(os.getenv("API_PORT", 8000)))

    # Prometheus
    prometheus_scrape_path: str = Field(
        default=os.getenv("PROMETHEUS_SCRAPE_PATH", "/metrics")
    )

    # Consumer batching
    consumer_s3_batch_size: int = Field(
        default=int(os.getenv("CONSUMER_S3_BATCH_SIZE", 500))
    )
    consumer_s3_batch_seconds: int = Field(
        default=int(os.getenv("CONSUMER_S3_BATCH_SECONDS", 30))
    )

    # Data paths
    sample_log_path: str = Field(
        default=os.getenv("SAMPLE_LOG_PATH", "/data/sample_logs/access.log")
    )

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()  # type: ignore[arg-type]
