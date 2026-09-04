import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any


class StructuredJsonFormatter(logging.Formatter):
    """
    Format standard Python log records into structured, machine-readable JSON strings.
    Extracts timestamps, severity, service context, and extra attributes for log collectors.
    """

    def __init__(self, service_name: str) -> None:
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        # Build base structured log payload
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include exception stack traces if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include custom extra metadata passed via logger.<level>(..., extra={...})
        standard_attrs = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
        }
        extras = {k: v for k, v in record.__dict__.items() if k not in standard_attrs}
        if extras:
            log_data["context"] = extras

        return json.dumps(log_data)


def setup_logging(service_name: str, log_level: str | None = None) -> logging.Logger:
    """
    Initialize root and service loggers with structured JSON formatting
    and standard stream handlers.
    Reads default severity from the LOG_LEVEL environment variable (defaults to INFO).
    """

    level_name = (log_level or os.getenv("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove pre-existing handlers to prevent duplicated log lines
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(StructuredJsonFormatter(service_name=service_name))
    root_logger.addHandler(stream_handler)

    # Silence overly verbose third-party engine loggers unless explicitly requested
    logging.getLogger("uvicorn.access").handlers = [stream_handler]
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logging.getLogger(service_name)


def get_logger(service_name: str) -> logging.Logger:
    """
    Retrieve or create a namespaced logger for a specific microservice component.
    """
    return logging.getLogger(service_name)
