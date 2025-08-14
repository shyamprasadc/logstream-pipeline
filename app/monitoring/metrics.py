from prometheus_client import Counter, Histogram

processed_records_total = Counter(
    "log_records_processed_total", "Total number of log records processed"
)
processing_errors_total = Counter(
    "log_records_errors_total", "Total number of errors while processing logs"
)
processing_latency_seconds = Histogram(
    "log_processing_latency_seconds", "Latency of parsing+storing per record"
)
