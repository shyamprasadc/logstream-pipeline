import logging
import os


def configure_logging(service_name: str) -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format=f"%(asctime)s | {service_name} | %(levelname)s | %(name)s | %(message)s",
    )
